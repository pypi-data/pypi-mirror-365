"""
Module dedicated to loading and managing models from the `timm` library.
"""

import timm
import torch


def load_timm_model(name="resnet50", device="cuda"):
    """
    Load a pre-trained model from the timm library and the associated preprocessing transform.

    Parameters
    ----------
    name : str, optional
        Name of the model to load (default is 'resnet50').
    device : str, optional
        Device on which to run the model (default is 'cuda').

    Returns
    -------
    preprocess : callable
        Preprocessing function to apply to input data before passing it to the model.
    model : torch.nn.Module
        The pre-trained model instance.
    """
    model = timm.create_model(name, pretrained=True).to(device)
    model.eval()

    cfg = timm.data.resolve_data_config(model.pretrained_cfg)
    preprocess = timm.data.create_transform(**cfg)

    return preprocess, model
