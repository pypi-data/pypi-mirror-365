"""
Module dedicated to facilitate the loading of some neuro datasets.
"""

import numpy as np
from brainscore_vision import load_benchmark


def load_majajhong2015_IT():
    """
    Load the Majaj & Hong 2015 IT benchmark dataset.
    This dataset contains neural responses from the IT cortex of macaque monkeys.

    Returns
    -------
    images_paths : list of str
        List of paths to the images used in the experiment.
    neural_data : np.ndarray
        Neural responses of shape (n_samples, n_neurons).
    labels : np.ndarray
        Labels corresponding to the images, indicating the object category.
    """
    benchmark = load_benchmark("MajajHong2015public.IT-pls")
    stimulus_set = benchmark._assembly.attrs["stimulus_set"]

    images_paths = [stimulus_set.get_stimulus(sid)
                    for sid in benchmark._assembly['stimulus_id'].values]
    neural_data = np.array(benchmark._assembly)
    labels = benchmark._assembly['object_name'].values

    return images_paths, neural_data, labels
