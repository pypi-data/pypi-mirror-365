import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.special import gamma

from mickelonius.core.stat.hypothesis_testing.stationarity import phillips_perron_test, adf_test


def fractional_weights(d: float, k_max: int, tolerance: float = 1e-5):
    """
    Compute fractional weights for given d and size.
    :param d:
    :param k_max:
    :param tolerance:
    """
    import math
    w = []
    for k in range(k_max):
        numerator = ((-1) ** k) * gamma(d + 1)

        denominator = gamma(k + 1) * gamma(d - k + 1)
        if not math.isnan(numerator) and not math.isnan(denominator):
            weight_value = numerator/denominator
            if abs(weight_value) >= tolerance:
                w.append(weight_value)
            else:
                break
        else:
            break
    return np.array(w)


def plot_weights(d_range, n_plots, k_max):
    """

    :param d_range: range of exponents to plot weights for
    :param n_plots: how many plot lines to generate
    :param k_max:
    :return:
    """
    w = pd.DataFrame()
    for d in np.linspace(d_range[0], d_range[1], n_plots):
        w_ = fractional_weights(d, k_max=k_max)
        w_ = pd.DataFrame(w_, index=range(w_.shape[0])[::-1], columns=[d])
        w = w.join(w_, how='outer')
    ax = w[2:].plot()
    ax.legend(loc='upper right')
    plt.show()


def relative_weight_loss(weights):
    """
    Compute relative weight loss, lambda_l, for a set of fractional weights.
    :param weights:
    """
    cumulative_weights = np.cumsum(np.abs(weights))
    relative_loss = np.abs(weights) / cumulative_weights
    return relative_loss


def optimal_lag(weights, threshold=0.01):
    """
    Determine the optimal lag length based on relative weight loss.
    :param weights:
    :param threshold:
    """
    rel_loss = relative_weight_loss(weights)
    for l, loss in enumerate(rel_loss):
        if loss < threshold:  # Stop when weight loss falls below the threshold
            return l
    return len(weights)  # If all weights are above the threshold


def fractional_differentiation(
    series: pd.Series,
    d: float,
    threshold: float = 0.01,
    window: str = "expanding",
    window_size: int = None,
    pad_leading_nans: bool = True
) -> pd.Series:
    """
    Perform fractional differentiation with support for expanding and fixed-width windows.

    Parameters:
    :param series: The time series to differentiate.
    :param d: Fractional differencing order.
    :param threshold: Threshold for relative weight loss (lambda_l).
    :param window: 'expanding' or 'fixed'.
    :param window_size: Size of the fixed window (required if window='fixed')
    :param pad_leading_nans: pad with nans to match len(series)
    :return: pd.Series
    """
    size = len(series)
    weights = fractional_weights(d, size)
    optimal_lag_length = optimal_lag(weights, threshold)
    truncated_weights = weights[:optimal_lag_length + 1]

    differentiated = []
    for i in range(len(series)):
        if window == "expanding":
            # Expanding window: Use all available lags up to the current time step
            start_idx = max(0, i - optimal_lag_length)
        elif window == "fixed" and window_size is not None:
            # Fixed-width window: Use only the specified number of lags
            start_idx = max(0, i - window_size + 1)
        else:
            raise ValueError("Invalid window type or missing window_size for fixed windowing.")

        # Extract the relevant slice of the series and weights
        slice_ = series[start_idx: i + 1]

        # get last len(slice_) elements of truncated weights
        applicable_weights = truncated_weights[-len(slice_):]

        # Match indices of two series
        k = min(slice_.shape[0], applicable_weights.shape[0])
        slice_ = slice_.iloc[:k]
        applicable_weights = applicable_weights[:k]

        # Compute the fractional difference value
        reversed_weights = applicable_weights[::-1]
        diff_value = np.dot(reversed_weights, slice_)

        differentiated.append(diff_value)

    # Pad with NaN to match the original series length
    if pad_leading_nans:
        nan_padding = optimal_lag_length if window == "expanding" else (window_size - 1)
        differentiated = [np.nan] * nan_padding + differentiated[nan_padding:]

    return pd.Series(differentiated, index=series.index)


def plot_min_ffd(
    input_series: pd.Series,
    frac_diff_type: str = "fixed",
    frac_diff_window: int = 10,
    weight_threshold: float = 0.01,
    stationarity_test: str = "phillips_perron",
    stat_significance_level: float = 0.05,
    stat_autolag: str = "AIC",
    stat_maxlag: int = None,
    stat_regression: str = "ct"
) -> None:
    """
    Plot stationarity test statistic and correlation w/ orig series vs. d
    - Lower stationarity statistic indicates stationarity, subject to significance levels
    - Higher correlation between frac diff'd series and orig series indicates info
    retention, maintaining fidelity with orig series
    :param stat_regression:
    :param stat_maxlag:
    :param stat_autolag:
    :param stat_significance_level:
    :param stationarity_test:
    :param weight_threshold:
    :param frac_diff_window:
    :param frac_diff_type:
    :param input_series:
    :return:
    """
    out = pd.DataFrame(columns=['testStat', 'pVal', 'lags', '95% conf', 'corr',])  # 'resid_autocorr'])

    for d in np.linspace(0.0, 1.0, 11):
        ffd_series = fractional_differentiation(
            input_series,
            d,
            window=frac_diff_type,
            window_size=frac_diff_window,
            threshold=weight_threshold,
        )

        # Mask to filter out NaN values in ffd_series
        valid_mask = ~np.isnan(ffd_series)

        # Filter both arrays to align valid values
        filtered_ffd_series = ffd_series[valid_mask]
        filtered_input_series = input_series[valid_mask]

        corr = np.corrcoef(filtered_ffd_series, filtered_input_series)[0, 1]
        if stationarity_test == "adf":
            s_test = adf_test(
                filtered_ffd_series,
                autolag=stat_autolag,
                maxlag=stat_maxlag,
                regression=stat_regression,
                significance_level=stat_significance_level
            )
        elif stationarity_test == "phillips_perron":
            s_test = phillips_perron_test(
                filtered_ffd_series,
                regression=stat_regression,
                significance_level=stat_significance_level
            )
        else:
             raise ValueError("Invalid stationarity test, must be 'adf' or 'phillips_perron'")

        out.loc[d] = [
            s_test["test_statistic"],
            s_test["p_value"],
            s_test["lags"],
            s_test["critical_values"]["5%"],
            corr
        ]

    fig, ax1 = plt.subplots()

    ax1.set_xlabel('d')
    ax1.set_ylabel('Correlation')
    p_corr = ax1.plot(out.index, out['corr'], color='black')
    ax1.tick_params(axis='both')

    ax2 = ax1.twinx()  # a second y-axis that shares the same x-axis

    test_stat_lbl = f"{'ADF' if stationarity_test=="adf" else 'Phillips-Perron'} Test Statistic"
    ax2.set_ylabel(test_stat_lbl)
    p_adf = ax2.plot(out.index, out['testStat'], color='red')
    ax2.axhline(out.loc[d]['95% conf'], color='red', linestyle='--', linewidth=0.8)
    ax2.tick_params(axis='both')

    # Legend for two axes
    leg = p_corr + p_adf  # p_autocorr
    labs = ['Corr', test_stat_lbl]  # 'Residual Autcorr',
    plt.legend(leg, labs, loc="lower left", framealpha=1)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.xticks(np.linspace(0, 1.0, 11))
    for x in np.linspace(0, 1.0, 11):
        ax2.axvline(x, color='gray', linestyle='-', linewidth=0.5)
        ax1.axhline(x, color='gray', linestyle='-', linewidth=0.5)

    plt.show()
