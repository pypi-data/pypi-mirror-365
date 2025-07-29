import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.diagnostic import acorr_ljungbox
from pandas.api.types import is_datetime64_any_dtype


def adf_test(
    series: pd.Series,
    significance_level: float = 0.05,
    autolag: str = "AIC",
    maxlag: int = None,
    regression: str = "ct"
):
    """
    Perform ADF test on a time series and return results.
    """
    adf_result = adfuller(
        series,
        autolag=autolag,
        maxlag=maxlag,
        regression=regression,)

    # Fit regression and get residuals
    y = series.diff().dropna()
    X = sm.add_constant(series.shift(1).iloc[1:])  # Include lagged y
    for i in range(1, adf_result[2] + 1):  # Add lagged differences
        X[f"lag_{i}"] = series.diff(i).shift(1).iloc[1:]
    X = X.dropna()
    if is_datetime64_any_dtype(X.index):
        X["trend"] = X.index.view('int64')
    else:
        X["trend"] = X.index - 1
    # y = y.loc[X.index]

    common_index = y.index.intersection(X.index)
    y = y.loc[common_index]
    X = X.loc[common_index]

    model = sm.OLS(y, X).fit()
    residuals = model.resid

    # Low autocorrelation in residuals is a positive indicator of a well-specified
    # regression model but does not directly speak to the stationarity of the original series.
    num_lags = int(len(residuals) ** (1 / 3))
    results = acorr_ljungbox(residuals, lags=[num_lags], return_df=True)
    residuals_autocorr = float(results.loc[num_lags]["lb_pvalue"])

    output = {
        'test_statistic': float(adf_result[0]),
        'p_value': float(adf_result[1]),
        "lags": num_lags,
        'critical_values': {k: float(v) for k, v in adf_result[4].items()},
        'stationary': bool(adf_result[1] < significance_level),
        'residuals': residuals,
        'residuals_autocorr_pvalue': residuals_autocorr,
    }
    return output