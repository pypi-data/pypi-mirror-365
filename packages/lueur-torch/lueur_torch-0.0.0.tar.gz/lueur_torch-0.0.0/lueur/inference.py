import torch


def batch_inference(images, inference_fn, transform, device="cuda", batch_size=32):
    """
    Apply a model to a list of PIL images in batches and return stacked features.

    Parameters
    ----------
    images : list of PIL.Image
        Input image list.
    inference_fn : callable
        Inference function to apply to each image.
    transform : callable
        Preprocessing transform to apply to each image.
    device : str
        Device for inference.
    batch_size : int
        Number of images per batch.

    Returns
    -------
    features : torch.Tensor
        Output features of shape (N, ...), stacked across all batches.
    """
    outputs = []

    with torch.no_grad():
        for i in range(0, len(images), batch_size):
            batch = [transform(img).unsqueeze(0) for img in images[i:i + batch_size]]
            tensor = torch.cat(batch).to(device)
            feats = inference_fn(tensor)
            outputs.append(feats)

    return torch.cat(outputs, dim=0).cpu()
