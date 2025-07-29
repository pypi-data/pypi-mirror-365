from datetime import timedelta

import pandas as pd
import numpy as np

from mickelonius.core.time_series.labelling import (
    get_triple_barrier_events,
    get_thresholded_events,
    get_vertical_barrier,
)
from mickelonius.core.time_series.features import (
    get_daily_vol,
)
from mickelonius.core.time_series.sampling import (
    get_num_co_events,
    get_sample_tw,
    get_indicator_matrix,
    get_avg_uniqueness,
    seq_bootstrap,
    sample_w_ret,
    get_time_decay
)


def test_get_triple_barrier_events(daily_spy_data):

    # Use average volatility to get event times
    daily_spy_data["vol"] = get_daily_vol(
        daily_spy_data,
        horizon=1,
        lookback=5
    )
    min_ret = daily_spy_data["vol"].mean()
    thresholded_events = get_thresholded_events(
        df=daily_spy_data,
        metric_threshold=2*min_ret,
        event_col="Close"
    )
    assert len(thresholded_events) == 323, \
        f'thresholded_events should have 323 events for {min_ret}, got {len(thresholded_events)}'

    # compute vertical barriers or time stops
    trgt = daily_spy_data["vol"].dropna()
    t1 = get_vertical_barrier(
        thresholded_events,
        daily_spy_data.Close,
        timedelta(days=10)
    )

    events = get_triple_barrier_events(
        t_series=daily_spy_data.Close,
        t_events=thresholded_events,
        profittake_stoploss=[1, 1],
        targets=trgt,
        min_ret=min_ret,
        vertical_barriers=t1
    )
    assert(len(events) == 248)
    assert not ((~events['event_stoploss'].isna() & ~events['event_profittake'].isna())).any(), \
        "Each row should have either event_stoploss or event_stoploss or neither, but not both"


def test_sampling(daily_spy_data):
    # Use average volatility to get event times
    vols = get_daily_vol(daily_spy_data, horizon=1)
    min_ret = vols.mean()
    t_events = get_thresholded_events(
        daily_spy_data,
        metric_threshold=2 * min_ret,
        event_col="Close"
    )
    print(f'{len(t_events)} events for {min_ret}')

    trgt = vols.dropna()
    t1 = get_vertical_barrier(
        t_events,
        daily_spy_data.Close,
        timedelta(days=10)
    )

    events = get_triple_barrier_events(
        t_series=daily_spy_data.Close,
        t_events=t_events,
        profittake_stoploss=[1, 1],
        targets=trgt,
        min_ret=min_ret,
        vertical_barriers=t1
    )
    print(f'{len(events)} events 1x vol')
    #sides = get_bins(events, test_df.Close)

    num_co_events = get_num_co_events(close_index=daily_spy_data.index, t1=events['t'], molecule=events.index)
    num_co_events = num_co_events.loc[~num_co_events.index.duplicated(keep='last')]  # de-dupe
    num_co_events = num_co_events.reindex(daily_spy_data.index).fillna(0)  # line up with price orig series, fill gaps with 0
    weights = get_sample_tw(molecule=events.index, t1=events['t'], num_co_events=num_co_events)

    t1_int = pd.Series([2, 3, 5, 11, 14, 16, 19, 21], index=[0, 2, 4, 7, 10, 12, 15, 18])  # t0, t1 for each feature obs
    bar_index = pd.DataFrame(index=range(t1_int.max() + 1))  # index of bars
    ind_m = get_indicator_matrix(bar_index.index, t1_int)

    # Random sample with replacement
    phi = np.random.choice(ind_m.columns, size=ind_m.shape[1])
    print('phi', phi)
    print('Standard uniqueness:', get_avg_uniqueness(ind_m[phi]).mean())

    # Sequential bootstrap sampling
    phi = seq_bootstrap(ind_m)
    print('phi', phi)
    print('Sequential uniqueness:', get_avg_uniqueness(ind_m[phi]).mean())

    ret_weights = sample_w_ret(t1, num_co_events, daily_spy_data.Close, events.index)

    ind_m_dt = get_indicator_matrix(daily_spy_data.index, t1)

    # time decay
    d = get_time_decay(weights, 1.0)
    print(d.iloc[0], d.iloc[-1])

    d = get_time_decay(weights, 0.5)
    print(d.iloc[0], d.iloc[-1])

    d = get_time_decay(weights, -0.25)
    print(d.iloc[0], d.iloc[-1])
    print(d.iloc[int(0.25 * len(d)) - 6])
    print(d.iloc[int(0.25 * len(d)) - 7])
    print(d.iloc[int(0.25 * len(d)) - 8])
    print('done')
