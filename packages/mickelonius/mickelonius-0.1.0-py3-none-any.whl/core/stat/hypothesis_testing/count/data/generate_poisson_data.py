import numpy as np
import pandas as pd


def generate_poisson_data(rate, size):
    """
    Generate Poisson-distributed count data.

    Parameters:
    rate (float): The rate (lambda) parameter of the Poisson distribution.
    size (int): The number of samples to generate.

    Returns:
    numpy.ndarray: Array of Poisson-distributed counts.
    """
    return np.random.poisson(rate, size)
