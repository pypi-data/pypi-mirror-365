# Copyright 2025 The IREE Authors
#
# Licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import logging
from collections import defaultdict
from dataclasses import dataclass
from math import prod
from typing import Optional

import sympy
import torch.fx as fx

from .._support.indexing import IndexExpr, IndexSequence, IndexSymbol
from .._support.tracing import CapturedTrace
from ..lang.global_symbols import *
from ..ops.wave_ops import (
    CustomOp,
    GatherToLDS,
    IndexSequence,
    Read,
    Write,
    get_custom,
)
from ..wave.constraints import (
    Constraint,
    TilingConstraint,
    WorkgroupConstraint,
)
from ..wave.utils.graph_utils import DCE
from .compile_options import WaveCompileOptions
from .minimize_global_loads import (
    materialize_shape,
    update_write_dependencies,
)
from .utils.general_utils import (
    ceildiv,
    delinearize_index,
    get_hardware_constraint,
    infer_dim,
    remove_thread_indexing,
    find_index_bounds,
)
from .utils.graph_utils import DCE
from .utils.symbol_utils import subs_idxc

logger = logging.getLogger(__name__)


def is_valid_read(node: fx.Node) -> bool:
    read = get_custom(node)
    if not isinstance(read, Read):
        return False

    if subs_idxc(read.memory_type.address_space) != GLOBAL_ADDRESS_SPACE:
        return False

    return True


def is_valid_write(write: CustomOp) -> bool:
    if not isinstance(write, Write):
        return False

    if subs_idxc(write.memory_type.address_space) != SHARED_ADDRESS_SPACE:
        return False

    if not write.has_identity_mapping():
        return False

    return True


def combine_index(
    index1: dict[IndexSymbol, IndexSequence],
    index2: dict[IndexSymbol, IndexSequence],
) -> dict[IndexSymbol, IndexSequence]:
    """
    This function takes two index sequences and combines them.
    """
    assert set(index1.keys()) == set(index2.keys())
    return {
        key: IndexSequence(
            index1[key].start + index2[key].start,
            sympy.Max(index1[key].size, index2[key].size),
            1,
        )
        for key in index2
    }


@dataclass
class GatherToSharedConfig:
    materialized_shape: list[IndexSymbol]
    elements_per_thread: int
    expected_number_of_loads: int


def get_gather_to_shared_config(
    read: Read,
    constraint_tile_size: dict[IndexSymbol, int],
    total_number_of_threads,
    element_type: "DataType",
    supported_load_widths: list[int],
    hardware_constraint: "HardwareConstraint",
    fastest_dim_bound: Optional[IndexExpr],
) -> Optional[GatherToSharedConfig]:
    """
    Get the gather to shared config for the given read and write.
    """
    logger.info(f"fastest_dim_bound={fastest_dim_bound}")

    bitwidth = element_type.bitwidth()
    logger.info(f"element_type={element_type}, bitwidth={bitwidth}")

    symbolic_shape = read.type.symbolic_shape
    logger.info(f"symbolic_shape={symbolic_shape}")

    store_elems_per_thread = hardware_constraint.max_elems_per_load(element_type)
    max_elements_per_store = total_number_of_threads * store_elems_per_thread
    logger.info(
        f"store_elems_per_thread={store_elems_per_thread}, "
        f"max_elements_per_store={max_elements_per_store}"
    )

    materialized_shape = materialize_shape(constraint_tile_size, symbolic_shape)
    logger.info(f"materialized_shape={materialized_shape}")

    total_number_of_elements = prod(materialized_shape)
    logger.info(f"total_number_of_elements={total_number_of_elements}")
    expected_number_of_loads = ceildiv(total_number_of_elements, max_elements_per_store)
    logger.info(f"expected_number_of_loads={expected_number_of_loads}")
    elements_per_thread = ceildiv(
        total_number_of_elements, expected_number_of_loads * total_number_of_threads
    )
    logger.info(f"elements_per_thread={elements_per_thread}")

    vector_width = elements_per_thread * bitwidth
    if fastest_dim_bound is not None:
        fastest_dim_bound = fastest_dim_bound * bitwidth

    # `vector_width` is the the vector size each thread loads.
    # `fastest_dim_bound` is the bound against which we are checking our loads,
    # it is larger than `vector_width` but it must be aligned with chosen load width.
    load_width = get_load_width(supported_load_widths, vector_width, fastest_dim_bound)
    if load_width is None:
        logger.info(
            f"No supported load width found for width={vector_width}, "
            f"fastest_dim_bound={subs_idxc(fastest_dim_bound)}"
        )
        return None

    logger.info(f"load_width={load_width}")

    # Get supported load width for the given bitwidth and if they are not
    # equal then we need to adjust the number of loads and elements per thread.
    ratio = vector_width // load_width
    logger.info(f"ratio={ratio}")
    expected_number_of_loads *= ratio
    elements_per_thread //= ratio

    if materialized_shape[-1] % elements_per_thread != 0:
        logger.info(
            f"materialized_shape[-1]={materialized_shape[-1]} is not divisible by "
            f"elements_per_thread={elements_per_thread}"
        )
        return None

    return GatherToSharedConfig(
        materialized_shape,
        elements_per_thread,
        expected_number_of_loads,
    )


def emit_global_to_lds(
    read: Read,
    write: Write,
    materialized_shape: list[IndexSymbol],
    elements_per_thread: int,
    expected_number_of_loads: int,
    total_number_of_threads: int,
    thread_id: IndexExpr,
    symbolic_shape: list[IndexSymbol],
    bounds: dict[IndexSymbol, IndexExpr],
    wave_subs: dict[IndexSymbol, IndexExpr],
    element_type: "DataType",
) -> defaultdict[fx.Node, list[Write]]:
    """
    Emit `GatherToLDS` for the given read and write.
    """
    elements_per_wave = elements_per_thread * total_number_of_threads
    logger.info(f"elements_per_wave={elements_per_wave}")

    # For index delinearization, assume our shape in `elements_per_thread` chunks.
    materialized_shape_adjusted = list(materialized_shape)
    materialized_shape_adjusted[-1] = materialized_shape[-1] // elements_per_thread

    logger.info(f"materialized_shape_adjusted={materialized_shape_adjusted}")

    # GatherToLDS writes `elements_per_wave` elements contiguously to LDS, so we
    # cannot have any padding if it crosses a array row boundary.
    drop_padding = materialized_shape[-1] % elements_per_wave != 0

    global_index = remove_thread_indexing(read.index)
    logger.info(f"global_index={global_index}")

    new_writes = defaultdict(list)
    for i in range(expected_number_of_loads):
        # As we adjusted our shape to be in `elements_per_thread` chunks, each
        # subsequent load will be `total_number_of_threads` elements apart.
        thread_id_adjusted = thread_id + i * total_number_of_threads
        nd_index = delinearize_index(thread_id_adjusted, materialized_shape_adjusted)
        logger.info(f"nd_index={nd_index}")
        write_index = {}
        for bound_expr, idx in zip(symbolic_shape, nd_index):
            last = bound_expr == symbolic_shape[-1]
            dim = infer_dim(bound_expr)

            idx = idx * elements_per_thread if last else idx
            size = elements_per_thread if last else 1
            stride = 1
            write_index[dim] = IndexSequence(idx, size, stride)

        read_index = combine_index(global_index, write_index)

        # GatherToLDS only uses write index from the first thread in wave,
        # so make the index wave-uniform, simplifying the calculation.
        write_index = {k: v.subs(wave_subs) for k, v in write_index.items()}

        logger.info(f"read_index={read_index}")
        logger.info(f"write_index={write_index}")
        with write.graph.inserting_before(write.fx_node):
            new_write = GatherToLDS(
                read.memory,
                write.memory,
                read_index,
                write_index,
                element_type,
                elements_per_thread,
                read.mapping,
                write.mapping,
                bounds,
            ).add_to_graph(write.graph)

            new_writes[write.memory].append(new_write)
            if drop_padding:
                custom_memory = get_custom(write.memory)
                padding = custom_memory.padding
                if padding != 0:
                    custom_memory.update_arg("padding", 0)
                    new_distributed_shape = list(custom_memory.distributed_shape)
                    new_distributed_shape[-1] -= padding
                    custom_memory.update_arg(
                        "distributed_shape", tuple(new_distributed_shape)
                    )

    return new_writes


def get_load_width(
    supported_load_widths: list[int],
    target_width: int,
    fastest_dim_bound: Optional[IndexExpr],
) -> Optional[int]:
    """
    Get the largest suitable load width for the given bitwidth.
    """
    for width in supported_load_widths[::-1]:
        if target_width % width != 0:
            continue

        if fastest_dim_bound is not None:
            # `subs_idxc` can return symbolic values which will also be != 0,
            # so we need to check `not (subs_idxc(...) == 0)`.
            if not (subs_idxc(fastest_dim_bound % width) == 0):
                continue

        return width

    return None


def gather_to_shared(
    trace: CapturedTrace,
    constraints: list[Constraint],
    options: WaveCompileOptions,
):
    """
    This pass enables direct memory load from global to lds without passing
    through register reducing the data movement. This instruction is supported
    only on specific architectures (gfx950).
    """
    if not options.use_global_to_shared:
        return

    logger.info("gather_to_shared")

    if "gfx94" not in options.target and "gfx95" not in options.target:
        logger.info("gather_to_shared not supported on this architecture")
        return

    id_to_read_write = defaultdict(list)
    for read in trace.walk(is_valid_read):
        read = get_custom(read)
        for write in read.users:
            if not is_valid_write(write):
                continue

            key = (read.pre_expansion_id, write.pre_expansion_id)
            id_to_read_write[key].append((read, write))

    if not id_to_read_write:
        return

    hardware_constraint = get_hardware_constraint(constraints)
    threads_per_wave = hardware_constraint.threads_per_wave
    waves_per_block = hardware_constraint.waves_per_block
    threads_per_block = hardware_constraint.threads_per_block
    total_number_of_threads = prod(threads_per_block)
    logger.info(f"total_number_of_threads={total_number_of_threads}")

    thread_id = hardware_constraint.linearized_thread_id

    # Make LDS write index to be wave-uniform by doing (THREAD_0 // 64) * 64
    wave_subs = {
        THREAD_0: (
            ((THREAD_0 // threads_per_wave) * threads_per_wave)
            if waves_per_block[0] > 1
            else 0
        ),
        THREAD_1: THREAD_1 if waves_per_block[1] > 1 else 0,
        THREAD_2: THREAD_2 if waves_per_block[2] > 1 else 0,
    }

    supported_load_widths = [32]

    if "gfx95" in options.target:
        supported_load_widths += [96, 128]

    constraint_tile_size = {
        c.dim: c.tile_size
        for c in constraints
        if isinstance(c, TilingConstraint) or isinstance(c, WorkgroupConstraint)
    }

    for reads_writes in id_to_read_write.values():
        read, write = reads_writes[0]
        logger.info(f"processing read={read}, write={write}")

        if not read.has_identity_mapping():
            logger.info("non-identity read mapping is not supported yet")
            continue

        assert read.index == write.index

        element_type = read.type.dtype

        symbolic_shape = read.type.symbolic_shape
        if read.bounds:
            bounds = read.bounds
        else:
            vector_shapes = read.vector_shapes or hardware_constraint.vector_shapes
            bounds = find_index_bounds(
                constraints, read.index, vector_shapes, symbolic_shape
            )

        logger.info(f"bounds={bounds}")
        fastest_dim_bound = bounds.get(symbolic_shape[-1], None) if bounds else None

        config = get_gather_to_shared_config(
            read,
            constraint_tile_size,
            total_number_of_threads,
            element_type,
            supported_load_widths,
            hardware_constraint,
            fastest_dim_bound,
        )

        if config is None:
            logger.info("no gather to shared config found")
            continue

        materialized_shape = config.materialized_shape
        elements_per_thread = config.elements_per_thread
        expected_number_of_loads = config.expected_number_of_loads

        new_writes = emit_global_to_lds(
            read,
            write,
            materialized_shape,
            elements_per_thread,
            expected_number_of_loads,
            total_number_of_threads,
            thread_id,
            symbolic_shape,
            bounds,
            wave_subs,
            element_type,
        )

        update_write_dependencies(new_writes, trace)

    DCE(trace)
