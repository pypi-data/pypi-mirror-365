"""
Module dedicated to extracting concepts using CRAFT method.
"""

import torch
from einops import rearrange
from overcomplete.optimization import NMF
from overcomplete.metrics import r2_score


def craft(activations, nb_concepts=50, device="cuda", solver="mu"):
    """
    Learn concept dictionary using Non-negative Matrix Factorization (NMF).
    Supports CNN or ViT-style activations.

    Parameters
    ----------
    activations : torch.Tensor
        Input tensor of shape (B, C, H, W) or (B, T, D).
    nb_concepts : int
        Number of concepts (dictionary atoms).
    device : str
        Device for computation.
    solver : str
        Solver for NMF ("mu", "cd", etc.).

    Returns
    -------
    Z_full : torch.Tensor
        Code tensor of shape (B, H, W, K) or (B, T, K).
    D : torch.Tensor
        Dictionary matrix of shape (K, C) or (K, D).
    r2 : float
        R² reconstruction score.
    """
    assert isinstance(activations, torch.Tensor), "Input must be a torch.Tensor"
    assert activations.amin() >= 0, "Input must be non-negative"
    assert activations.ndim in {3, 4}, "Input must be 3D (B, T, D) or 4D (B, C, H, W)"

    if activations.ndim == 4:
        # cnn style: (b, c, h, w) with b is batch, c channels, h height and w width
        # and we learn the dictionary over c
        b, c, h, w = activations.shape
        A = activations.to(device).float()

        A_flat = rearrange(A, "b c h w -> (b h w) c")
        def unflatten(Z): return rearrange(Z, "(b h w) k -> b h w k", b=b, h=h, w=w)

    else:
        # vit style: (b, t, d) with b is batch, t tokens and d dimensions
        # and we learn the dictionary over d
        b, t, d = activations.shape
        A = activations.to(device).float()

        A_flat = rearrange(A, "b t d -> (b t) d")
        def unflatten(Z): return rearrange(Z, "(b t) k -> b t k", b=b, t=t)

    nmf = NMF(nb_concepts=nb_concepts, solver=solver, device=device)
    Z, D = nmf.fit(A_flat)

    Z_full = unflatten(Z)
    score = r2_score(A_flat, Z @ D).item()

    return Z_full, D, score
