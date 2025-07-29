"""
Utility functions for Lueur.
"""

import numpy as np
import torch


def to_npf32(tensor):
    """
    Check if tensor is torch, ensure it is on CPU and convert to NumPy.

    Parameters
    ----------
    tensor : torch.Tensor or np.ndarray
        Input tensor.
    """
    # return as is if already npf32
    if isinstance(tensor, np.ndarray) and tensor.dtype == np.float32:
        return tensor
    # torch case
    if isinstance(tensor, torch.Tensor):
        return tensor.detach().cpu().numpy().astype(np.float32)
    # pil case (and other)
    return np.array(tensor).astype(np.float32)


def clip_percentile(heatmap, percentile=99, max_only=True):
    """
    Clip the heatmap values to a specified percentile.

    Parameters
    ----------
    heatmap : np.ndarray or torch.Tensor
        Input heatmap tensor.
    percentile : float, optional
        Percentile value to clip at (default is 99).
        Clip the values at (100-p, p) if max_only is False. Else at (0, p).
    max_only : bool, optional
        If True, only clip the maximum values (default is True).

    Returns
    -------
    np.ndarray
        Clipped heatmap tensor.
    """
    assert 0 < percentile < 100, "Percentile must be between 0 and 100."

    heatmap = to_npf32(heatmap)
    if max_only:
        clip_min = None
    else:
        clip_min = np.percentile(heatmap, 100 - percentile)

    clip_max = np.percentile(heatmap, percentile)
    heatmap = np.clip(heatmap, clip_min, clip_max)

    return heatmap
