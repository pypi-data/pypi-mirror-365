from datetime import timedelta
from mickelonius.core.time_series.features import compute_raw_delta_t, compute_return


def test_compute_raw_delta_t(daily_spy_data):
    compute_raw_delta_t(daily_spy_data, col='Close')
    assert (daily_spy_data['Close'].diff() - daily_spy_data['delta_Close']).sum() < 0.00000001
    assert (daily_spy_data['t'].diff()[1:] - (daily_spy_data.index[1:]-daily_spy_data.index[:daily_spy_data.shape[0]-1])).sum() == timedelta(0)


def test_compute_return_horizon(daily_spy_data):
    col = 'Close'
    test_horizon = timedelta(minutes=10)
    compute_return(daily_spy_data, price_column=col, horizon=test_horizon)
    expected_return = daily_spy_data[col].rolling(test_horizon).apply(lambda x: (x.iloc[-1] - x.iloc[0])/x.iloc[0])
    assert (expected_return - daily_spy_data.reset_index(drop=True)[f'Return_{col}']).sum() < 0.0000001
    assert all(daily_spy_data['t0'] <= daily_spy_data.index)


def test_compute_return_no_horizon(daily_spy_data):
    col = 'Close'
    delta_col = f'delta_{col}'
    compute_raw_delta_t(daily_spy_data, col=col)
    compute_return(daily_spy_data, price_column=col)
    expected_return = daily_spy_data[delta_col]/daily_spy_data[col].shift(1)
    assert (expected_return - daily_spy_data.reset_index(drop=True)[f'Return_{col}']).sum() < 0.0000001
    assert all(daily_spy_data['t0'] <= daily_spy_data.index)


# def test_compute_raw_delta_t_dask(feature_test_df_dask):
#     df = compute_raw_delta_t(feature_test_df_dask, col='Value')
#     assert (df['Value'].diff().fillna(0) - df['delta_Value']).sum().compute() < 0.00000001
#     assert (df['t'].diff() - feature_test_df_dask['t'].diff()).sum().compute() == timedelta(0)


# def test_compute_return_horizon_dask(feature_test_df_dask):
#     col = 'Value'
#     test_horizon = timedelta(minutes=10)
#     df = compute_return(feature_test_df_dask, col=col, horizon=test_horizon).compute()
#     expected_return = feature_test_df_dask[col].rolling(test_horizon).apply(lambda x: (x.iloc[-1] - x.iloc[0])/x.iloc[0], raw=False).compute()
#     assert (expected_return - df.reset_index()[f'Return_{col}']).sum() < 0.0000001
#     assert all(feature_test_df_dask['t0'].compute() <= df.index)


# def test_compute_return_no_horizon_dask(feature_test_df_dask):
#     col = 'Value'
#     delta_col = 'delta_Value'
#     df_delta = compute_raw_delta_t(feature_test_df_dask, col='Value').compute()
#     df = compute_return(feature_test_df_dask, col='Value').compute()
#     expected_return = df_delta[delta_col]/df_delta[col].shift(1)
#     # assert (expected_return - df[f'Return_{col}'].compute()).sum() < 0.0000001
#     assert (expected_return - df.reset_index()[f'Return_{col}']).sum() < 0.0000001
#     assert all(feature_test_df_dask['t0'].compute() <= df.index)
