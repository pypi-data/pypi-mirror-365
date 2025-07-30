#  Copyright (c) NXAI GmbH.
#  This software may be used and distributed according to the terms of the NXAI Community License Agreement.

import jax
import jax.numpy as jnp
import jax_triton as jt
import triton

from ....triton.chunkwise.limit_chunk.bw_kernel_recurrent import (
    mlstm_chunkwise__recurrent_bw_dC_kernel,
)
from ....triton.kernel_param_heuristics import get_head_dim_block_size
from ....utils.kernels import is_power_of_2
from ...stride_utils import get_stride
from ...utils import jax2triton_dtype


def mlstm_chunkwise__recurrent_bw_dC(
    matQ: jax.Array,  # (B, NH, S, DHQK)
    vecB: jax.Array,  # (B, NH, NC, L)
    scaM_inter: jax.Array,  # (B, NH, NC+1)
    vecM_combine: jax.Array,  # (B, NH, S)
    matDeltaH: jax.Array,  # (B, NH, S, DHHV)
    vecN_out: jax.Array,  # (B, NH, S)
    matDeltaC_last: jax.Array | None = None,  # (B, NH, DHQK, DHHV)
    qk_scale: float | None = None,
    CHUNK_SIZE: int = 64,
    NUM_CHUNKS: int = 1,
    EPS: float = 1e-6,
) -> jax.Array:  # matDeltaC_states (B, NH, (NC+1) * DHQK, DHHV)
    """
    Computes only the deltaC gradients for the backward pass.

    The other gradients are computed in the other (kernel) function.
    We do not need to compute the gradients for the denominator, as it cancels out in the forward in the groupnorm.

    Args:
        matQ: Tensor containing the query vectors. Shape (B, NH, S, DHQK).
        vecB: Tensor containing the summed log forget gate activations. Shape (B, NH, NC, L).
        scaM_inter: States of the M scalar. Shape (B, NH, NC+1).
        vecM_combine: Combined M states. Shape (B, NH, S).
        matDeltaH: Tensor containing the H gradients. Shape (B, NH, S, DHHV).
        vecN_out: States of the N vector. Shape (B, NH, NC * DHQK).
        matDeltaC_last: Tensor containing the last C gradients. Shape (B, NH, DHQK, DHHV).
            Defaults to None.
        qk_scale: Scale factor for the QK matrix. Defaults to None.
        CHUNK_SIZE: Chunk size. Defaults to 64.
        NUM_CHUNKS: Number of chunks. Defaults to 1.
        EPS: Epsilon value. Defaults to 1e-6.

    Returns:
        Tensor containing the C gradients. Shape (B, NH, (NC+1) * DHQK, DHHV).
    """
    B, NH, S, DHQK, DHHV = *matQ.shape, matDeltaH.shape[-1]
    NC = NUM_CHUNKS
    L = CHUNK_SIZE
    _dtype = matQ.dtype

    assert NC == vecB.shape[2], "Number of chunks must match the number in vecB."
    assert L == vecB.shape[3], "Chunk size must match the chunk size in vecB."
    assert is_power_of_2(L), "Chunk size must be a power of 2."

    if qk_scale is None:
        qk_scale = DHQK**-0.5

    USE_LAST_STATE = matDeltaC_last is not None

    matDeltaC_states = jax.ShapeDtypeStruct(
        shape=(B, NH, (NC + 1) * DHQK, DHHV), dtype=jnp.float32
    )
    if matDeltaC_last is None:
        matDeltaC_last = jnp.zeros((1,), dtype=_dtype)

    siz_b_DHQK = get_head_dim_block_size(head_dim=DHQK, min_block_size=64)
    siz_b_DHHV = get_head_dim_block_size(head_dim=DHHV, min_block_size=64)

    num_b_DHQK = triton.cdiv(DHQK, siz_b_DHQK)
    num_b_DHHV = triton.cdiv(DHHV, siz_b_DHHV)

    num_stages = 1
    num_warps = 4 if siz_b_DHQK == 64 else 2

    grid = (num_b_DHQK, num_b_DHHV, B * NH)
    matDeltaC_states = jt.triton_call(
        matQ,
        vecB,
        scaM_inter,
        vecM_combine,
        matDeltaH,
        vecN_out,
        matDeltaC_last,
        out_shape=matDeltaC_states,
        qk_scale=qk_scale,
        str_matQ_B_NH=get_stride(matQ, axis=1),
        str_matQ_S=get_stride(matQ, axis=2),
        str_matQ_DHQK=get_stride(matQ, axis=3),
        str_vecB_B_NH=get_stride(vecB, axis=1),
        str_vecB_NC=get_stride(vecB, axis=2),
        str_vecB_L=get_stride(vecB, axis=3),
        str_scaM_inter_B_NH=get_stride(scaM_inter, axis=1),
        str_scaM_inter_NC=get_stride(scaM_inter, axis=2),
        str_vecM_combine_B_NH=get_stride(vecM_combine, axis=1),
        str_vecM_combine_S=get_stride(vecM_combine, axis=2),
        str_matDeltaH_B_NH=get_stride(matDeltaH, axis=1),
        str_matDeltaH_S=get_stride(matDeltaH, axis=2),
        str_matDeltaH_DHHV=get_stride(matDeltaH, axis=3),
        str_vecN_out_B_NH=get_stride(vecN_out, axis=1),
        str_vecN_out_S=get_stride(vecN_out, axis=2),
        str_matDeltaC_last_B_NH=get_stride(matDeltaC_last, axis=1)
        if USE_LAST_STATE
        else 0,
        str_matDeltaC_last_DHQK=get_stride(matDeltaC_last, axis=2)
        if USE_LAST_STATE
        else 0,
        str_matDeltaC_last_DHHV=get_stride(matDeltaC_last, axis=3)
        if USE_LAST_STATE
        else 0,
        str_matDeltaC_states_B_NH=get_stride(matDeltaC_states, axis=1),
        str_matDeltaC_states_NCDHQK=get_stride(matDeltaC_states, axis=2),
        str_matDeltaC_states_DHHV=get_stride(matDeltaC_states, axis=3),
        B=B,
        NH=NH,
        S=S,
        DHQK=DHQK,
        DHHV=DHHV,
        NC=NC,
        L=L,
        siz_b_DHQK=siz_b_DHQK,
        siz_b_DHHV=siz_b_DHHV,
        USE_LAST_STATE=USE_LAST_STATE,
        DTYPE=jax2triton_dtype(_dtype),
        EPS=EPS,
        num_stages=num_stages,
        num_warps=num_warps,
        grid=grid,
        kernel=mlstm_chunkwise__recurrent_bw_dC_kernel,
    )

    return matDeltaC_states
