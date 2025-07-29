import pandas as pd
import statsmodels.api as sm
from arch.unitroot import PhillipsPerron
from statsmodels.stats.diagnostic import acorr_ljungbox
from pandas.api.types import is_datetime64_any_dtype

def phillips_perron_test(
        series: pd.Series,
        significance_level: float = 0.05,
        regression: str = "ct"
) -> dict:
    pp_test = PhillipsPerron(series, trend=regression)
    test_stat = pp_test.stat
    p_value = pp_test.pvalue
    lags = pp_test.lags
    n_obs = pp_test.nobs
    crit_values = pp_test.critical_values

    # Fit regression and get residuals
    y = series.diff().dropna()
    X = sm.add_constant(series.shift(1).iloc[1:])  # Include lagged y
    for i in range(1, lags + 1):
        X[f"lag_{i}"] = series.diff(i).shift(1).iloc[1:]
    X = X.dropna()
    if is_datetime64_any_dtype(X.index):
        X["trend"] = X.index.view('int64')
    else:
        X["trend"] = X.index - 1

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

    return {
        "test_statistic": float(test_stat),
        "p_value": float(p_value),
        "lags": lags,
        "critical_values": {k: float(v) for k, v in crit_values.items()},
        "stationary": bool(p_value < significance_level),
        'residuals': residuals,
        'residuals_autocorr_pvalue': residuals_autocorr,
    }
