import dask.dataframe as dd
import pandas as pd
from datetime import timedelta

from mickelonius.core.time_series.features import get_daily_vol, compute_return
from mickelonius.core.time_series.labelling import (
    get_thresholded_events,
    get_vertical_barrier,
    apply_triple_barrier,
)


def test_get_t_events_intra_horizon(daily_spy_data):
    min_ret = 0.025
    t_events = get_thresholded_events(
        daily_spy_data,
        min_ret,
        'Close',
        timedelta(minutes=10)
    )
    compute_return(
        daily_spy_data,
        'Close',
        timedelta(minutes=10)
    )
    assert all(daily_spy_data[daily_spy_data['Return_Close'].abs() > min_ret].t0 == t_events.index)


def test_get_t_events_intra_horizon_dask(daily_spy_data_dask):
    min_ret = 0.025
    t_events = get_thresholded_events(
        daily_spy_data_dask,
        min_ret,
        'Close',
        timedelta(days=10)
    ).compute()
    compute_return(
        daily_spy_data_dask,
        'Close',
        timedelta(days=10)
    )
    df = daily_spy_data_dask.compute()
    assert all(df[df['Return_Close'].abs() > min_ret].t0 == t_events.index)


def test_get_t_events_intra_horizon_dask_pandas_match(
        daily_spy_data, daily_spy_data_dask
):
    min_ret = 0.025
    t_events_dask = get_thresholded_events(
        daily_spy_data_dask,
        min_ret,
        'Close',
        timedelta(days=10)
    ).compute()
    t_events = get_thresholded_events(
        daily_spy_data,
        min_ret,
        'Close',
        timedelta(days=10)
    )
    assert t_events.shape == t_events_dask.shape
    assert all(t_events.index == t_events_dask.index)
    assert all(t_events.Return_Close == t_events_dask.Return_Close)


def test_get_t_events_horizon(daily_spy_data):
    vols = get_daily_vol(daily_spy_data, horizon=4)
    min_ret = vols.mean()
    t_events = get_thresholded_events(daily_spy_data, min_ret, 'Close', timedelta(days=4))
    compute_return(daily_spy_data, 'Close', timedelta(days=4))
    assert all(daily_spy_data[daily_spy_data['Return_Close'].abs() > min_ret].t0 == t_events.index)


def test_get_t_events_no_horizon(daily_spy_data):
    vols = get_daily_vol(daily_spy_data, horizon=4)
    min_ret = vols.mean()
    t_events = get_thresholded_events(daily_spy_data, min_ret, 'Close')
    compute_return(daily_spy_data, 'Close')
    filtered_rets = daily_spy_data.dropna()[daily_spy_data['Return_Close'].abs() > min_ret].set_index('t0')

    assert all(filtered_rets.index == t_events.index)


def test_get_t_events_horizon_dask_pandas_match(
        daily_spy_data, daily_spy_data_dask
):
    vols = get_daily_vol(daily_spy_data, horizon=4)
    min_ret = vols.mean()
    t_events = get_thresholded_events(daily_spy_data, min_ret, 'Close')
    t_events_dask = get_thresholded_events(daily_spy_data_dask, min_ret, 'Close').compute()
    assert t_events.shape == t_events_dask.shape
    assert all(t_events.index == t_events_dask.index)
    assert all(t_events.Return_Close == t_events_dask.Return_Close)


def test_get_vertical_barrier(daily_spy_data):
    min_ret = 0.025
    t_events = get_thresholded_events(
        daily_spy_data,
        min_ret,
        'Close',
        timedelta(days=4)
    )
    t_max = daily_spy_data.index.max()
    vb0 = pd.Series(data=t_events.index, index=t_events.index)
    vb0 = vb0.apply(lambda x: min(x + timedelta(days=10), t_max))

    vb = get_vertical_barrier(t_events, daily_spy_data.Close, timedelta(days=10))

    assert all(vb == vb0)


# def test_get_vertical_barrier_dask(daily_spy_data_dask):
#     min_ret = 0.025
#     t_events = get_thresholded_events(
#         daily_spy_data_dask,
#         min_ret,
#         'Close',
#         timedelta(days=4)
#     )
#     t_max = daily_spy_data_dask.index.max().compute()
#     t_idx = t_events.index.compute()
#     vb0 = pd.Series(data=t_idx, index=t_idx)
#     vb0 = vb0.apply(lambda x: min(x + timedelta(days=10), t_max))
#
#     vb = get_vertical_barrier(t_events, daily_spy_data_dask.Close, timedelta(days=10)).compute()
#
#     assert all(vb == vb0)


def test_triple_barrier(daily_spy_data):
    min_ret = 0.025
    t_events = get_thresholded_events(
        daily_spy_data,
        min_ret,
        'Close',
        timedelta(days=4)
    )
    compute_return(daily_spy_data, 'Close')
    t_events['vertical_barrier'] = get_vertical_barrier(t_events,
                                                        daily_spy_data.Close,
                                                        timedelta(days=30))
    t_events['horizontal_width'] = 1.0

    tbs = apply_triple_barrier(
        daily_spy_data[['Return_Close']],
        t_events,
        (0.03, 0.01)
    )

    time_stops = tbs[tbs['barrier'] == 'TIME_STOP']
    assert all(time_stops['ret_barrier'] < 0.03) and all(time_stops['ret_barrier'] > -0.01)
    profit_takes = tbs[tbs['barrier'] == 'PROFIT_TAKE']
    assert all(profit_takes['ret_barrier'] > 0.03)
    stop_losses = tbs[tbs['barrier'] == 'STOP_LOSS']
    assert all(stop_losses['ret_barrier'] < -0.01)


# TODO: functional but slow.... better way to do this w/ Dask?
# def test_triple_barrier_dask(daily_spy_data_dask):
#
#     client = None
#     try:
#         min_ret = 0.015
#         t_events_dask = get_thresholded_events(daily_spy_data_dask, min_ret, 'Close', timedelta(days=4))
#
#         compute_return(daily_spy_data_dask, 'Close')
#         t_events_dask['vertical_barrier'] = get_vertical_barrier(t_events_dask,
#                                                                  daily_spy_data_dask.Close,
#                                                                  timedelta(days=30))
#         t_events_dask['horizontal_width'] = 1.0
#         # t_events_dask = t_events_dask.repartition(6)
#
#         tbs = apply_triple_barrier(
#             daily_spy_data_dask[['Return_Close']],
#             t_events_dask,
#             (0.03, 0.01),
#         ).compute()
#
#         time_stops = tbs[tbs['barrier'] == 'TIME_STOP']
#         assert all(time_stops['ret_barrier'] < 0.03) and all(time_stops['ret_barrier'] > -0.01)
#         profit_takes = tbs[tbs['barrier'] == 'PROFIT_TAKE']
#         assert all(profit_takes['ret_barrier'] > 0.03)
#         stop_losses = tbs[tbs['barrier'] == 'STOP_LOSS']
#         assert all(stop_losses['ret_barrier'] < -0.01)
#
#     finally:
#         pass #client.close()


def test_triple_barrier_intra(daily_spy_data):
    min_ret = 0.025
    t_events = get_thresholded_events(
        daily_spy_data,
        min_ret,
        'Close',
        timedelta(days=4)
    )
    compute_return(daily_spy_data, 'Close')
    t_events['vertical_barrier'] = get_vertical_barrier(t_events,
                                                        daily_spy_data.Close,
                                                        timedelta(days=30))
    t_events['horizontal_width'] = 1.0

    tbs = apply_triple_barrier(
        daily_spy_data[['Return_Close']],
        t_events,
        (0.03, 0.01),
        col='Close'
    )

    time_stops = tbs[tbs['barrier'] == 'TIME_STOP']
    assert all(time_stops['ret_barrier'] < 0.03) and all(time_stops['ret_barrier'] > -0.01)
    profit_takes = tbs[tbs['barrier'] == 'PROFIT_TAKE']
    assert all(profit_takes['ret_barrier'] > 0.03)
    stop_losses = tbs[tbs['barrier'] == 'STOP_LOSS']
    assert all(stop_losses['ret_barrier'] < -0.01)


# def test_triple_barrier_intra_dask(feature_test_df_dask, t_events_dask):
#     rets = compute_return(feature_test_df_dask, 'Value')
#     t_events_dask['vertical_barrier'] = get_vertical_barrier(t_events_dask,
#                                                         feature_test_df_dask.Value,
#                                                         timedelta(days=30))
#     t_events_dask['horizontal_width'] = 1.0
#
#     tbs = apply_triple_barrier(
#         rets[['Return_Value']],
#         t_events_dask,
#         (0.03, 0.01),
#         col='Value'
#     ).compute()
#
#     time_stops = tbs[tbs['barrier'] == 'TIME_STOP']
#     assert all(time_stops['ret_barrier'] < 0.03) and all(time_stops['ret_barrier'] > -0.01)
#     profit_takes = tbs[tbs['barrier'] == 'PROFIT_TAKE']
#     assert all(profit_takes['ret_barrier'] > 0.03)
#     stop_losses = tbs[tbs['barrier'] == 'STOP_LOSS']
#     assert all(stop_losses['ret_barrier'] < -0.01)