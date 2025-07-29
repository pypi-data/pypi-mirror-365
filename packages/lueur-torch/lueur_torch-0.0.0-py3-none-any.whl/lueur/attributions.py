"""
Module dedicated to Attributions methods.
"""

import torch
import torch.nn.functional as F


RISE_MASKS = (torch.rand(16_000, 9, 9) > 0.5).float().cpu()


def saliency(imgs, score_fn):
    """
    Compute standard saliency map (absolute input gradients).

    Parameters
    ----------
    imgs : torch.Tensor
        Input batch of shape (N, C, H, W), requires_grad will be set in-place.
    score_fn : callable
        Function mapping input images to scalar scores (e.g., logits[:, class_id]).

    Returns
    -------
    saliency_map : torch.Tensor
        Tensor of shape (N, H, W), aggregated over channels.
    """
    assert len(imgs.shape) == 4, "Input tensor must be 4D (N, C, H, W)"
    imgs = imgs.requires_grad_()
    scores = score_fn(imgs).sum()
    scores.backward()

    # saliency map is the absolute value of the gradients
    # averaged over the channels
    heatmaps = imgs.grad.abs().mean(dim=1)
    return heatmaps


def gradient_input(imgs, score_fn):
    """
    Compute gradient x input attribution.

    Parameters
    ----------
    imgs : torch.Tensor
        Input tensor (N, C, H, W).
    score_fn : callable
        Scoring function for backpropagation.

    Returns
    -------
    attributions : torch.Tensor
        Tensor of shape (N, H, W).
    """
    assert len(imgs.shape) == 4, "Input tensor must be 4D (N, C, H, W)"

    grads = saliency(imgs, score_fn)

    heatmaps = imgs.abs() * grads.unsqueeze(1)
    heatmaps = heatmaps.mean(dim=1)

    return heatmaps.detach()


def smoothgrad(imgs, score_fn, n_samples=50, sigma=0.2, device="cuda"):
    """
    Compute SmoothGrad attribution by averaging saliency over noisy copies.

    Parameters
    ----------
    imgs : torch.Tensor
        Input tensor (N, C, H, W).
    score_fn : callable
        Function mapping input to scalar scores.
    n_samples : int
        Number of noisy samples to average.
    sigma : float
        Standard deviation of Gaussian noise.
    device : str
        Device for computation.

    Returns
    -------
    heatmaps : torch.Tensor
        Tensor of shape (N, H, W).
    """
    assert len(imgs.shape) == 4, "Input tensor must be 4D (N, C, H, W)"

    noise = torch.randn(n_samples, *imgs.shape[1:], device=device) * sigma
    maps = []

    for x in imgs:
        noisy = x.unsqueeze(0) + noise
        noisy.requires_grad_()
        sa = saliency(noisy, score_fn)
        maps.append(sa.mean(dim=0))

    heatmaps = torch.stack(maps)
    return heatmaps.detach()


def _rise(img, score_fn, batch_size=256, nb_masks=None, device="cuda"):
    """
    Internal RISE computation for a single image.

    Parameters
    ----------
    img : torch.Tensor
        Tensor of shape (C, H, W).
    score_fn : callable
        Scoring function.
    batch_size : int
        Number of masks per batch.
    nb_masks : int
        Total number of masks to use.
    device : str
        Device to use.

    Returns
    -------
    heatmap : torch.Tensor
        Attribution map of shape (H, W).
    """
    assert len(img.shape) == 3, "Input tensor must be 3D (C, H, W)"

    if nb_masks is None:
        nb_masks = RISE_MASKS.shape[0]

    masks = RISE_MASKS[:nb_masks].to(device)[:, None]
    h, w = img.shape[-2:]
    den = torch.zeros(h, w, device=device)
    num = torch.zeros(h, w, device=device)

    for i in range(0, nb_masks, batch_size):
        batch = masks[i:i + batch_size]
        batch = F.interpolate(batch, size=(h + 32, w + 32), mode="bicubic", align_corners=False, antialias=True)
        batch = batch[:, :, 16:-16, 16:-16]
        masked = img.unsqueeze(0) * batch
        with torch.no_grad():
            scores = score_fn(masked)
        den += batch.sum(dim=(0, 1))
        num += (batch * scores[:, None, None, None]).sum(dim=(0, 1)).squeeze()

    return (num / (den + 1e-6)).cpu()


def rise(imgs, score_fn, batch_size=256, nb_masks=8000, device="cuda"):
    """
    RISE attribution method.

    Parameters
    ----------
    imgs : torch.Tensor
        Input tensor (N, C, H, W).
    score_fn : callable
        Scoring function.
    batch_size : int
        Mask processing batch size.
    nb_masks : int
        Number of random binary masks to use.
    device : str
        Device for computation.

    Returns
    -------
    heatmaps : torch.Tensor
        Tensor of shape (N, H, W).
    """
    assert len(imgs.shape) == 4, "Input tensor must be 4D (N, C, H, W)"

    with torch.no_grad():
        heatmaps = torch.stack([_rise(x, score_fn, batch_size, nb_masks, device) for x in imgs])

    return heatmaps
