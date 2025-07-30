#  Copyright (c) NXAI GmbH.
#  This software may be used and distributed according to the terms of the NXAI Community License Agreement.

"""Triton backend for the forward and backward pass of the mLSTM chunkwise formulation.

In this file, we use the following notation:

Dimensions:
    B: batch size
    NH: number of heads
    S: sequence length (K, V)
    T: sequence length (Q)
    DHQK: hidden dimension (Q, K)
    DHHV: hidden dimension (H, V)
    NC: number of chunks
    L: chunk size

Variables:
    vecA, a: forward gate contribution, contribution of forget gates from last chunk state C_{k-1} to
            current timestep t
    vecB, b: backward gate contribution, contribution of forget and input gates up to next chunk
            state C_k (form current timestep t)
    scaG, g: "go through" gate contribution, contribution of forget gates from C_{k-1} to C_k.
    matD, D: gating matrix for the parallel form.
"""

from collections.abc import Callable

import jax
import jax.numpy as jnp

from .bw import mlstm_chunkwise_bw
from .fw import mlstm_siging_chunkwise_fw

# TODO if we want to tune the kernel parameters we need to pass it through the forward and backward functions
# See the pytorch wrapper for an example of how to do this.


def _mlstm_chunkwise_fwbw_generator(
    autocast_kernel_dtype: jnp.dtype = jnp.bfloat16,
    return_last_states: bool = False,
    recompute_states_in_bw: bool = True,
    chunk_size: int = 128,
    normalize: bool = True,
    eps: float = 1e-6,
) -> Callable[
    [jax.Array, jax.Array, jax.Array, jax.Array, jax.Array, jax.Array, jax.Array],
    tuple[jax.Array, jax.Array, jax.Array],
]:
    """
    Generate a forward and backward pass function for the mLSTM kernels with chunkwise formulation.

    Args:
        autocast_kernel_dtype: The dtype to use for the kernel computation. All inputs arguments up to vecF
            are cast to this dtype. vecF is automatically casted to float32 in the kernels.
        return_last_states: Whether to return the last states of the mLSTM.
        recompute_states_in_bw: Whether to recompute the mLSTM states in the backward pass.
        chunk_size: The chunk size to use for the mLSTM computation.
        eps: The epsilon value to use for numerical stability.

    Returns:
        A function that computes the forward pass of the mLSTM chunkwise formulation, which custom gradients for the
        backward pass. The function input signatures is:

            forward(
                matQ: jax.Array,  # (B, NH, S, DHQK)
                matK: jax.Array,  # (B, NH, S, DHQK)
                matV: jax.Array,  # (B, NH, S, DHV)
                vecI: jax.Array,  # (B, NH, S)
                vecF: jax.Array,  # (B, NH, S)
                matC_initial: jax.Array | None = None,  # (B, NH, DHQK, DHV)
                vecN_initial: jax.Array | None = None,  # (B, NH, DHQK)
            ) -> tuple[jax.Array, jax.Array, jax.Array]:
        The function returns the output of the mLSTM computation, and the last states internal states of C, N and M.
    """

    @jax.custom_gradient
    def forward(
        matQ: jax.Array,  # (B, NH, S, DHQK)
        matK: jax.Array,  # (B, NH, S, DHQK)
        matV: jax.Array,  # (B, NH, S, DHV)
        vecI: jax.Array,  # (B, NH, S)
        vecF: jax.Array,  # (B, NH, S)
        matC_initial: jax.Array | None = None,  # (B, NH, DHQK, DHV)
        vecN_initial: jax.Array | None = None,  # (B, NH, DHQK)
    ) -> tuple[jax.Array, jax.Array, jax.Array]:
        B, NH, S, DHQK = matQ.shape
        qk_scale = DHQK**-0.5
        # Verify shapes to prevent errors in the kernels.
        assert matK.shape == (
            B,
            NH,
            S,
            DHQK,
        ), f"matK shape {matK.shape} does not match matQ shape {matQ.shape}."
        assert matV.shape[:-1] == (
            B,
            NH,
            S,
        ), f"matV shape {matV.shape} does not match matQ shape {matQ.shape}."
        assert vecI.shape == (
            B,
            NH,
            S,
        ), f"vecI shape {vecI.shape} does not match matQ shape {matQ.shape}."
        assert vecF.shape == (
            B,
            NH,
            S,
        ), f"vecF shape {vecF.shape} does not match matQ shape {matQ.shape}."
        # Verify initial states shapes.
        if matC_initial is not None:
            assert (
                matC_initial.shape
                == (
                    B,
                    NH,
                    DHQK,
                    matV.shape[-1],
                )
            ), f"matC_initial shape {matC_initial.shape} does not match matQ shape {matQ.shape}."
        if vecN_initial is not None:
            assert (
                vecN_initial.shape
                == (
                    B,
                    NH,
                    DHQK,
                )
            ), f"vecN_initial shape {vecN_initial.shape} does not match matQ shape {matQ.shape}."
        # Cast to autocast_kernel_dtype. Exclude vecF as it is automatically upcasted to float32 in kernels.
        orig_dtypes = {
            "q": matQ.dtype,
            "k": matK.dtype,
            "v": matV.dtype,
            "i": vecI.dtype,
            "f": vecF.dtype,
        }
        matQ = matQ.astype(autocast_kernel_dtype)
        matK = matK.astype(autocast_kernel_dtype)
        matV = matV.astype(autocast_kernel_dtype)
        vecI = vecI.astype(autocast_kernel_dtype)
        if matC_initial is not None:
            orig_dtypes["c"] = matC_initial.dtype
            matC_initial = matC_initial.astype(autocast_kernel_dtype)
        if vecN_initial is not None:
            orig_dtypes["n"] = vecN_initial.dtype
            vecN_initial = vecN_initial.astype(autocast_kernel_dtype)
        # Call the forward triton kernels for the mLSTM.
        matH_out, vecN_out, last_states, all_states = mlstm_siging_chunkwise_fw(
            matQ=matQ,
            matK=matK,
            matV=matV,
            vecI=vecI,
            vecF=vecF,
            matC_initial=matC_initial,
            vecN_initial=vecN_initial,
            qk_scale=qk_scale,
            return_last_states=return_last_states,
            return_all_states=(not recompute_states_in_bw),
            normalize=normalize,
            chunk_size=chunk_size,
            eps=eps,
        )
        # Select what to return.
        if return_last_states:
            (matC_last, vecN_last) = last_states
        else:
            (matC_last, vecN_last) = (None, None)
        # Verify saved states.
        if all_states is not None:
            matC_all, vecN_all = all_states
        else:
            matC_all, vecN_all = (None, None)

        def backward(
            grad_list: tuple[jax.Array, jax.Array, jax.Array],
        ) -> tuple[
            jax.Array,
            jax.Array,
            jax.Array,
            jax.Array,
            jax.Array,
            jax.Array | None,
            jax.Array | None,
        ]:
            """Backward function with reverse function signature of forward."""
            # Read out gradients for individual forward outputs.
            matDeltaH, matDeltaC_last, _ = grad_list
            # Call the backward triton kernels for the mLSTM.
            (
                matDeltaQ,
                matDeltaK,
                matDeltaV,
                vecDeltaI,
                vecDeltaF,
                matDeltaC_initial,
                vecDeltaN_initial,
            ) = mlstm_chunkwise_bw(
                matQ=matQ,
                matK=matK,
                matV=matV,
                vecI=vecI,
                vecF=vecF,
                matC_initial=matC_initial,
                vecN_initial=vecN_initial,
                matC_all=matC_all,
                vecN_all=vecN_all,
                vecN_out=vecN_out,
                matDeltaH=matDeltaH,
                matDeltaC_last=matDeltaC_last,
                qk_scale=qk_scale,
                normalize=normalize,
                chunk_size=chunk_size,
                eps=eps,
            )
            # Cast back to original dtypes.
            matDeltaQ = matDeltaQ.astype(orig_dtypes["q"])
            matDeltaK = matDeltaK.astype(orig_dtypes["k"])
            matDeltaV = matDeltaV.astype(orig_dtypes["v"])
            vecDeltaI = vecDeltaI.astype(orig_dtypes["i"])
            vecDeltaF = vecDeltaF.astype(orig_dtypes["f"])
            if matDeltaC_initial is not None and "c" in orig_dtypes:
                matDeltaC_initial = matDeltaC_initial.astype(orig_dtypes["c"])
            if vecDeltaN_initial is not None and "n" in orig_dtypes:
                vecDeltaN_initial = vecDeltaN_initial.astype(orig_dtypes["n"])
            # Return gradients.
            return (
                matDeltaQ,
                matDeltaK,
                matDeltaV,
                vecDeltaI,
                vecDeltaF,
                matDeltaC_initial,
                vecDeltaN_initial,
            )

        return (matH_out, matC_last, vecN_last), backward

    return forward


def _get_chunkwise_fwbw_kernel(autocast_kernel_dtype: jnp.dtype, **kwargs) -> Callable:
    """
    Get the forward and backward pass function for the mLSTM kernels with chunkwise formulation.

    Args:
        autocast_kernel_dtype: The dtype to use for the kernel computation. All inputs arguments up to vecF
            are cast to this dtype. vecF is automatically casted to float32 in the kernels.
        **kwargs: Additional keyword arguments to pass to the kernel function.

    Returns:
        A function that computes the forward pass of the mLSTM chunkwise formulation, which custom gradients for the
        backward pass. See _mlstm_chunkwise_fwbw_generator for the function signature.
    """
    if autocast_kernel_dtype in [
        "float32",
        "float16",
        "bfloat16",
        jnp.float32,
        jnp.float16,
        jnp.bfloat16,
    ]:
        return _mlstm_chunkwise_fwbw_generator(autocast_kernel_dtype, **kwargs)
    else:
        raise ValueError(f"Unsupported kernel dtype {autocast_kernel_dtype}.")


def mlstm_siging_chunkwise__xl_chunk(
    q: jax.Array,
    k: jax.Array,
    v: jax.Array,
    i: jax.Array,
    f: jax.Array,
    c_initial: jax.Array | None = None,
    n_initial: jax.Array | None = None,
    return_last_states: bool = False,
    eps: float = 1e-6,
    normalize: bool = True,
    chunk_size: int = 128,
    autocast_kernel_dtype: jnp.dtype = jnp.float32,
) -> jax.Array | tuple[jax.Array, tuple[jax.Array, jax.Array, jax.Array]]:
    """
    Apply the mLSTM chunkwise formulation with Triton kernels.

    Supports autograd application.

    Args:
        q: The query tensor of shape (B, NH, S, DHQK).
        k: The key tensor of shape (B, NH, S, DHQK).
        v: The value tensor of shape (B, NH, S, DHV).
        i: The input gate preactivation tensor of shape (B, NH, S).
        f: The forget gate preactivation tensor of shape (B, NH, S).
        c_initial: The initial chunk state tensor of shape (B, NH, DHQK, DHV).
        n_initial: The initial chunk state tensor of shape (B, NH, DHQK).
        return_last_states: Whether to return the last states of the mLSTM.
        eps: The epsilon value to use for numerical stability.
        normalize: Whether to normalize the C state in the mLSTM.
        chunk_size: The chunk size to use for the mLSTM computation.
        autocast_kernel_dtype: The dtype to use for the kernel computation. All inputs arguments up
            to vecF are cast to this dtype. vecF is automatically casted to float32 in the kernels.

    Returns:
        The output of the mLSTM computation. If return_last_states is True, the last states of the
        mLSTM are also returned.
    """
    _mlstm_chunkwise_fwbw = _get_chunkwise_fwbw_kernel(
        autocast_kernel_dtype,
        return_last_states=return_last_states,
        recompute_states_in_bw=True,
        chunk_size=chunk_size,
        normalize=normalize,
        eps=eps,
    )
    matH_out, matC_last, vecN_last = _mlstm_chunkwise_fwbw(
        q,
        k,
        v,
        i,
        f,
        c_initial,
        n_initial,
    )
    if return_last_states:
        return matH_out, (matC_last, vecN_last)
    else:
        return matH_out
