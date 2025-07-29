import numpy as np
import pandas as pd

from mickelonius.core.stat.hypothesis_testing.stationarity import phillips_perron_test
from mickelonius.core.time_series.frac_diff import (
    plot_min_ffd,
    fractional_differentiation,
    fractional_weights,
)

# TODO: Implement FFD fractional differencing in dask and make quantitative tests for frac diff


def test_fractional_weights():
    n = int(1e3)
    tol = 1e-5
    for d in np.linspace(0, 1.0, 11):
        w = fractional_weights(d, k_max=n)
        assert np.all(np.abs(w[~np.isnan(w)]) > tol)
        assert np.all(~np.isnan(w))


def test_frac_diff_expand_no_pad_sp(daily_spy_data):
    s_test = phillips_perron_test(daily_spy_data['Close'])
    assert not s_test["stationary"]

    d = 0.4
    fdf = fractional_differentiation(
        daily_spy_data['Close'],
        d,
        pad_leading_nans=False
    )
    assert fdf.shape == daily_spy_data['Close'].shape

    s_test = phillips_perron_test(fdf)
    assert s_test["stationary"]


def test_frac_diff_expand_no_pad_syn(nonstationary_series):
    time_series = nonstationary_series
    fdf = fractional_differentiation(
        time_series,  # daily_spy_data["Close"],
        d=0.5,
        threshold=0.01,
        window="expanding",
        window_size=None,
        pad_leading_nans=False
    )
    assert fdf.shape == time_series.shape

    s_test = phillips_perron_test(fdf)
    assert s_test["stationary"]


def test_frac_diff_fixed_no_pad_syn(nonstationary_series):
    time_series = nonstationary_series

    s_test = phillips_perron_test(time_series)
    assert not s_test["stationary"]

    fdf = fractional_differentiation(
        time_series,
        d=0.5,
        threshold=0.01,
        window="fixed",
        window_size=10,
        pad_leading_nans=False
    )
    assert fdf.shape == time_series.shape

    s_test = phillips_perron_test(fdf)
    assert s_test["stationary"]


def test_plot_min_ffd(nonstationary_series):
    plot_min_ffd(nonstationary_series)


def test_plot_min_ffd_spy(daily_spy_data):
    plot_min_ffd(daily_spy_data['Close'], stationarity_test="phillips_perron")
    plot_min_ffd(daily_spy_data['Close'], stationarity_test="adf")
