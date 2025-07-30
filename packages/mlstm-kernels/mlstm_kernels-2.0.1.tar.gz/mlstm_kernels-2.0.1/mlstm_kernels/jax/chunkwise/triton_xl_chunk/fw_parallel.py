#  Copyright (c) NXAI GmbH.
#  This software may be used and distributed according to the terms of the NXAI Community License Agreement.

import jax
import jax.numpy as jnp
import jax_triton as jt
import triton

from ....triton.chunkwise.xl_chunk.fw_kernel_parallel import (
    mlstm_chunkwise__parallel_fw_Hintra_kernel,
)
from ....triton.kernel_param_heuristics import get_head_dim_block_size
from ....utils.kernels import is_power_of_2
from ...stride_utils import get_stride
from ...utils import jax2triton_dtype
from .chunkwise_gates import compute_chunkwise_log_gates_vecB


def mlstm_chunkwise__parallel_fw_Hintra(
    matQ: jax.Array,  # (B, NH, S, DHQK)
    matK: jax.Array,  # (B, NH, S, DHQK)
    matV: jax.Array,  # (B, NH, S, DHHV)
    vecI: jax.Array,  # (B, NH, NC * L) = (B, NH, S)
    vecF: jax.Array,  # (B, NH, NC * L) = (B, NH, S)
    # these are all the states at every chunk, (we only use NC states up to the last chunk, i.e. :-1)
    matC_all: jax.Array,  # (B, NH, (NC+1) * DHQK, DHHV)
    vecN_all: jax.Array,  # (B, NH, (NC+1) * DHQK)
    scaM_all: jax.Array,  # (B, NH, (NC+1))
    qk_scale: float | None = None,
    chunk_size: int = 64,
    siz_b_LQ: int = 32,
    siz_b_LKV: int = 32,
    siz_b_DHQK: int | None = None,
    siz_b_DHHV: int | None = None,  # DHHV blocksize for each thread block
    num_warps: int | None = None,
    num_stages: int | None = None,
    eps: float = 1e-6,
    output_dtype: jnp.dtype = jnp.float32,
) -> tuple[
    jax.Array, jax.Array, jax.Array
]:  # matH_out (B, NH, S, DHHV), vecN_out (B, NH, S), vecM_out (B, NH, S)
    """
    Execute the parallel forward kernel for the H computation in the mLSTM chunkwise formulation.

    This function defines the grid and block sizes for the kernel launch and calls the kernel. See
    the fwbw backend implementation and the triton kernels for more information.
    chunk parallel size:        siz_b_LQ
    chunk loop size:            siz_b_LKV
    head dim parallel size:     siz_b_DHHV
    head dim loop size:         siz_b_DHQK

    Args:
        matQ: Tensor containing the queries. Shape (B, NH, S, DHQK).
        matK: Tensor containing the keys. Shape (B, NH, S, DHQK).
        matV: Tensor containing the values. Shape (B, NH, S, DHHV).
        matC_states: States of the C matrix. Shape (B, NH, NC * DHQK, DHHV).
            This state and following states must be all states up to the last chunk, i.e. :-1.
        vecN_states: States of the N vector. Shape (B, NH, NC * DHQK).
        scaMinter_states: States of the M scalar. Shape (B, NH, NC).
        vecI: Tensor containing the input gate. Shape (B, NH, NC, L).
        vecF: Tensor containing the forget gate preactivations. Shape (B, NH, NC * L) = (B, NH, S).
        qk_scale: Scaling factor for the QK matrix. Defaults to None and will be inferred.
        CHUNK_SIZE: Chunk size for the kernel. Defaults to 64.
        NUM_CHUNKS: Number of chunks. Defaults to 1.
        EPS: Small value to avoid division by zero. Defaults to 1e-6.

    Returns:
        Tuple containing the output matrix H (shape (B, NH, S, DHHV)) and the N vector (shape (B, NH, S)).
    """
    B, NH, S, DHQK = matK.shape
    DHHV = matV.shape[-1]

    assert (
        S % chunk_size == 0
    ), f"Sequence length {S} must be divisible by chunk size {chunk_size}"
    NC = S // chunk_size
    L = chunk_size

    assert is_power_of_2(L), "Chunk size must be a power of 2."

    if qk_scale is None:
        qk_scale = DHQK**-0.5

    siz_b_DHQK = (
        get_head_dim_block_size(head_dim=DHQK, min_block_size=64)
        if siz_b_DHQK is None
        else siz_b_DHQK
    )

    if siz_b_DHHV is None:
        siz_b_DHHV = get_head_dim_block_size(head_dim=DHHV, min_block_size=128)
    else:
        siz_b_DHHV = siz_b_DHHV

    assert siz_b_LQ <= L, "siz_b_LQ must be less than or equal to chunk size L"
    assert siz_b_LKV <= L, "siz_b_LKV must be less than or equal to chunk size L"
    assert siz_b_LKV <= siz_b_LQ, "siz_b_LKV must be less than or equal to siz_b_LQ"
    assert siz_b_LQ % siz_b_LKV == 0, "siz_b_LQ must be divisible by siz_b_LKV"
    num_b_DHHV = triton.cdiv(DHHV, siz_b_DHHV)
    num_b_LQ = triton.cdiv(L, siz_b_LQ)

    num_stages = 1 if num_stages is None else num_stages
    if num_warps is None:
        num_warps = 4 if siz_b_DHQK >= 64 else 2

    vecB = compute_chunkwise_log_gates_vecB(vecF=vecF, chunk_size=chunk_size)

    # Prepare the output shapes.
    matH_out = jax.ShapeDtypeStruct((B, NH, S, DHHV), matQ.dtype)
    vecN_out = jax.ShapeDtypeStruct((B, NH, S), jnp.float32)
    vecM_out = jax.ShapeDtypeStruct((B, NH, S), jnp.float32)

    # Define the grid and call the triton kernel.
    grid = (num_b_DHHV, num_b_LQ, NC * B * NH)
    matH_out, vecN_out, vecM_out = jt.triton_call(
        matQ,  # (B, NH, S, DHQK)
        matK,  # (B, NH, S, DHQK)
        matV,  # (B, NH, S, DHHV)
        matC_all,  # (B, NH, NC * DHQK, DHHV)
        vecN_all,  # (B, NH, NC * DHQK)
        scaM_all,  # (B, NH, NC)
        vecI,  # (B, NH, NC, L)
        vecB,  # (B, NH, NC, L)
        out_shape=(matH_out, vecN_out, vecM_out),
        qk_scale=qk_scale,
        str_matQK_B_NH=get_stride(matQ, axis=1),
        str_matQK_S=get_stride(matQ, axis=2),
        str_matQK_DHQK=get_stride(matQ, axis=3),
        str_matHV_B_NH=get_stride(matV, axis=1),
        str_matHV_S=get_stride(matV, axis=2),
        str_matHV_DHHV=get_stride(matV, axis=3),
        str_matCstates_B_NH=get_stride(matC_all, axis=1),
        str_matCstates_NCDHQK=get_stride(matC_all, axis=2),
        str_matCstates_DHHV=get_stride(matC_all, axis=3),
        str_vecNstates_B_NH=get_stride(vecN_all, axis=1),
        str_vecNstates_NCDHQK=get_stride(vecN_all, axis=2),
        str_scaMinterstates_B_NH=get_stride(scaM_all, axis=1),
        str_vecBI_B_NH=get_stride(vecB, axis=1),
        str_vecBI_NC=get_stride(vecB, axis=2),
        str_vecBI_L=get_stride(vecB, axis=3),
        str_vecMN_B_NH=get_stride(vecN_out, axis=1),
        str_vecMN_S=get_stride(vecN_out, axis=2),
        B=B,
        NH=NH,
        S=S,
        DHQK=DHQK,
        DHHV=DHHV,
        NC=NC,
        L=L,
        siz_b_LQ=siz_b_LQ,
        siz_b_LKV=siz_b_LKV,
        siz_b_DHQK=siz_b_DHQK,
        siz_b_DHHV=siz_b_DHHV,
        DTYPE=jax2triton_dtype(matQ.dtype),
        OUTPUT_DTYPE=jax2triton_dtype(output_dtype.dtype),
        EPS=eps,
        MINIMUM_MAX_VAL=-10.0,
        num_stages=num_stages,
        num_warps=num_warps,
        grid=grid,
        kernel=mlstm_chunkwise__parallel_fw_Hintra_kernel,
    )

    return matH_out, vecN_out, vecM_out
