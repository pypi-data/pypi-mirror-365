import numpy as np
import pandas as pd

from mickelonius.core.stat.hypothesis_testing.stationarity import adf_test, phillips_perron_test

np.random.seed(42)
data = np.cumsum(np.random.randn(100))
non_stationary_series = pd.Series(data)
stationary_series = non_stationary_series.diff().dropna()


def test_adf():
    adf_result = adf_test(stationary_series)
    assert adf_result["stationary"]

    adf_ns_result = adf_test(non_stationary_series)
    assert not adf_ns_result["stationary"]


def test_pp():
    pp_result = phillips_perron_test(stationary_series)
    assert pp_result["stationary"]

    pp_ns_result = phillips_perron_test(non_stationary_series)
    assert not pp_ns_result["stationary"]
