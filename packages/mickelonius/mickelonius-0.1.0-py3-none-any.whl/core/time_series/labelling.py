from dask import dataframe as dd
from typing import Union, List, Tuple, Callable, Optional
from datetime import timedelta, datetime

import pandas as pd
import numpy as np

from mickelonius.core.time_series.features import compute_return


def get_triple_barrier_events(
    t_series: Union[pd.Series, dd.Series],
    t_events: Union[pd.DataFrame, dd.DataFrame],
    profittake_stoploss: List[int],
    targets: Union[pd.Series, dd.Series],
    min_ret: float,
    vertical_barriers: Optional[Union[pd.Series, dd.Series]] = None,
    side: Optional[Union[pd.Series, dd.Series]]= None
):
    """
    Finds time of first barrier touch. Note that when side field is present in events dataframe,
    it is the case that the desired side is set by an exogenous model or an operator/PM. This is
    also known as meta-labelling by Lopez de Prado.
    :param t_series: Pandas Series of prices with DatetimeIndex
    :param t_events: Pandas Series with DatetimeIndex that contains timestamps that will seed every
    triple barrier
    :param profittake_stoploss: List of two non-negative float values:
        profittake_stoploss[0]: Sets width of upper barrier (0 for no upper barrier)
        profittake_stoploss[1]: Set width of lower barrier (0 for no lower barrier)
    :param targets: Pandas series of targets, expressed as returns with DatetimeIndex
    :param min_ret: Min target return required for running a triple barrier search
    :param vertical_barriers: Pandas Series of Timestamps, representing the vertical time barrier for each
     event, with DatetimeIndex. If None, no time stop/barrier.
    :param side: Pandas Series indicating side as meta-labels. If None
    :return:Pandas dataframe with columns:
        vertical_barrier: timestamp of vertical barrier
        target: target return used to generate horizontal barrier(s)
        t: time of touch
    """
    # get target
    targets = targets.reindex(t_events.index)
    targets = targets[targets > min_ret]

    # get t1 (max hold period)
    if vertical_barriers is None:
        vertical_barriers = pd.Series(pd.NaT, index=targets.index)

    # form events object, apply stop loss on t1
    if side is not None:
        side_ = side
    else:
        side_ = pd.Series(1., index=targets.index)

    events = pd.concat({
        'vertical_barrier': vertical_barriers,
        'target': targets,
        'side': side_
    }, axis=1).dropna(subset=['target'])

    df0 = apply_pt_sl_on_events(t_series, events, profittake_stoploss, events.index, first_touch=True)

    def get_touch_time(row):
        if not pd.isna(row.event_stoploss):
            return row.event_stoploss
        elif not pd.isna(row.event_profittake):
            return row.event_profittake
        else:
            return row.vertical_barrier

    df0['t'] = df0.apply(get_touch_time, axis=1)

    if side is None:
        df0 = df0.drop('side', axis=1)

    return df0


def apply_pt_sl_on_events(
        close,
        events,
        profittake_stoploss,
        molecule,
        first_touch=False
):
    """
    Triple-barrier labelling method, with two horizontal barriers (profit-take and stop-loss
    and one optional vertical barrier representing a stop loss
    :param close: Pandas series of prices
    :param events: Pandas dataframe with columns:
        vertical_barrier: timestamp of vertical barrier
        target: UNIT WIDTH of horizontal barriers
        side: [optional] for meta-labelling
    :param profittake_stoploss: List of two non-negative float values:
        profittake_stoploss[0]: Sets unit width of upper barrier (0 for no upper barrier)
        profittake_stoploss[1]: Sets unit width of lower barrier (0 for no lower barrier)
    :param molecule: list with subset of event indices for single thread
    :param first_touch: toggle only one, stop-loss or profit-take, but not both
    :return: Pandas dataframe where
        —out.index is event's starttime
        —out[’event_t_end’] is event's endtime
        —out[’event_target’] is event's target
        —out[’event_stoploss’] time, if any, stop loss hit
        —out[’event_profittake’] time, if any, profit take hit
        -out['event_return'] return when barrier hit
        -out['event_side'] [optional] for meta-labelling
    """
    # Apply stop loss/profit take, if it takes place before t1 (end of event)
    events_ = events.loc[molecule]
    out = events_.copy(deep=True)

    if profittake_stoploss[0] > 0:
        pt = profittake_stoploss[0] * events_['target']
    else:
        pt = pd.Series(index=events.index)

    if profittake_stoploss[1] > 0:
        s1 = -profittake_stoploss[1] * events_['target']
    else:
        s1 = pd.Series(index=events.index)

    for t0, t1 in events_['vertical_barrier'].fillna(close.index[-1]).items():

        # path prices
        df0 = close[(close.index >= t0) & (close.index < t1)]

        # path returns
        df0 = (df0/close[t0] - 1)*events_.at[t0, 'side']

        # earliest stop loss
        out.loc[t0, 'event_stoploss'] = df0[df0 < s1[t0]].index.min()

        # earliest profit take
        out.loc[t0, 'event_profittake'] = df0[df0 > pt[t0]].index.min()

        # return
        if (not pd.isna(out.loc[t0, 'event_stoploss']) and
            not pd.isna(out.loc[t0, 'event_profittake'])):
            if out.loc[t0, 'event_stoploss'] < out.loc[t0, 'event_profittake']:
                out.loc[t0, 'r'] = df0[out.loc[t0, 'event_stoploss']]
            else:
                out.loc[t0, 'r'] = df0[out.loc[t0, 'event_profittake']]
        elif (not pd.isna(out.loc[t0, 'event_stoploss']) and
              pd.isna(out.loc[t0, 'event_profittake'])):
            out.loc[t0, 'r'] = df0[out.loc[t0, 'event_stoploss']]
        elif (not pd.isna(out.loc[t0, 'event_profittake']) and
              pd.isna(out.loc[t0, 'event_stoploss'])):
            out.loc[t0, 'r'] = df0[out.loc[t0, 'event_profittake']]
        elif df0.size > 0:
            out.loc[t0, 'r'] = df0.iloc[-1]
        else:
            out.loc[t0, 'r'] = pd.NA

    if first_touch:
        out.loc[out['event_profittake'] < out['event_stoploss'], 'event_stoploss'] = pd.NaT
        out.loc[out['event_stoploss'] < out['event_profittake'], 'event_profittake'] = pd.NaT

    return out


def get_vertical_barrier(
        t_events: Union[pd.DataFrame, dd.DataFrame],
        close: Union[pd.Series, dd.Series],
        forward_window: timedelta
    ) -> Union[pd.Series, dd.Series]:
    """
    Get time stops, based on time_series or calendar days
    :param t_events: Pandas DatetimeIndex indicating each start time
    :param close: Pandas Series with DatetimeIndex and price time series
    :param forward_window: time window to look forward
    :return: Pandas Series where index is date and value is vertical barrier (i.e. time stop)
    """
    t_max = close.index.max()
    if isinstance(t_events, pd.DataFrame):
        vertical_barrier = pd.Series(data=t_events.index, index=t_events.index)
        vertical_barrier = vertical_barrier.apply(lambda x: min(x + forward_window, t_max))
    elif isinstance(t_events, dd.DataFrame):
        t_max = t_max.compute()
        vertical_barrier = t_events.index + forward_window
        vertical_barrier = vertical_barrier.map(lambda x: min(x, t_max))
        vertical_barrier_series = dd.from_dask_array(
            vertical_barrier.to_dask_array(),
            index=t_events.index,
            columns='t0'
        )
        return vertical_barrier_series


    else:
        raise RuntimeError('t_events parameter must be pandas.DataFrame or dask.dataframe.DataFrame')
    return vertical_barrier


def apply_triple_barrier(x: Union[pd.Series, dd.Series],
                         events: Union[pd.DataFrame, dd.DataFrame],
                         profittake_stoploss: Union[List, Tuple],
                         col: str = None
                         ):
    """
    Triple-barrier labelling method, with two horizontal barriers (profit-take and stop-loss
    and one optional vertical barrier representing a stop loss
    :param x: Pandas or Dask DataFrame
    :param events: Pandas dataframe with columns:
        (index): timestamp of event start
        vertical_barrier: timestamp of vertical barrier, can be pd.NaT
        horizontal_width: UNIT WIDTH of horizontal barriers
        side: [optional] for meta-labelling
    :param profittake_stoploss: List of two non-negative float values:
        profittake_stoploss[0]: Sets unit width of upper barrier (0 for no upper barrier)
        profittake_stoploss[1]: Sets unit width of lower barrier (0 for no lower barrier)

    :return: Pandas dataframe where
                     t0: event's starttime
            t_time_stop:
          ret_time_stop: return @ t_time_stop
            t_stop_loss:
          ret_stop_loss: return @ t_stop_loss
          t_profit_take:
        ret_profit_take: return @ t_profit_take
                barrier: which barrier was hit: STOP_LOSS, PROFIT_TAKE, TIME_STOP, NO_TRADE
            ret_barrier: return @ barrier hit
                   side: [optional] for meta-labelling
    """
    # TODO: need to use 'horizontal_width' to modulate stop loss/profit takes
    # if profittake_stoploss[0] > 0:
    #     events['profit_take_level'] = profittake_stoploss[0] * events['horizontal_width']
    # else:
    #     events['profit_take_level'] = pd.Series(index=events.index)
    #
    # if profittake_stoploss[1] > 0:
    #     events['stop_level'] = -profittake_stoploss[1] * events['horizontal_width']
    # else:
    #     events['stop_level'] = pd.Series(index=events.index)

    if col is None:
        col = 'Close'
    ret_col = f'Return_{col}'

    def get_barrier_hit(evt, x):
        t0 = evt.name
        t1 = evt['vertical_barrier']

        # Cumulative return trajectory
        # df0 = x[(x.index > t0) & (x.index <= t1)].fillna(0).cumsum()
        df0 = x[(x.index > t0) & (x.index <= t1)][ret_col].cumsum()

        t_stop_loss = df0[df0 < -profittake_stoploss[1]].index.min()
        if pd.isnull(t_stop_loss):
            ret_stop_loss = np.nan
        else:
            ret_stop_loss = df0.loc[t_stop_loss]

        t_profit_take = df0[df0 > profittake_stoploss[0]].index.min()
        if pd.isnull(t_profit_take):
            ret_profit_take = np.nan
        else:
            ret_profit_take = df0.loc[t_profit_take]

        if len(df0) > 0 and not pd.isnull(t1):
            ret_time_stop = df0.iloc[-1]
        else:
            ret_time_stop = np.nan

        if len(df0) > 0:
            if not pd.isnull(t_stop_loss) and not pd.isnull(t_profit_take):
                if t_stop_loss < t_profit_take:
                    barrier = 'STOP_LOSS'
                    ret_barrier = ret_stop_loss
                else:
                    barrier = 'PROFIT_TAKE'
                    ret_barrier = ret_profit_take
            elif pd.isnull(t_stop_loss) and not pd.isnull(t_profit_take):
                barrier = 'PROFIT_TAKE'
                ret_barrier = ret_profit_take
            elif not pd.isnull(t_stop_loss) and pd.isnull(t_profit_take):
                barrier = 'STOP_LOSS'
                ret_barrier = ret_stop_loss
            elif not pd.isnull(t1):
                barrier = 'TIME_STOP'
                ret_barrier = ret_time_stop
            else:
                barrier = 'NO_TRADE'
                ret_barrier = np.nan
        else:
            barrier = 'NO_TRADE'
            ret_barrier = np.nan

        return {
            't0': t0,
            't_time_stop': t1,
            'ret_time_stop': ret_time_stop,
            't_stop_loss': t_stop_loss,
            'ret_stop_loss': ret_stop_loss,
            't_profit_take': t_profit_take,
            'ret_profit_take': ret_profit_take,
            'barrier': barrier,
            'ret_barrier': ret_barrier,
        }

    if isinstance(events, dd.DataFrame):
        ee = events.apply(
            get_barrier_hit,
            axis='columns',
            result_type='expand',
            raw=False,
            args=(x,),
            meta={
                't0': 'datetime64[ns]',
                't_time_stop': 'datetime64[ns]',
                'ret_time_stop': 'float64',
                't_stop_loss': 'datetime64[ns]',
                'ret_stop_loss': 'float64',
                't_profit_take': 'datetime64[ns]',
                'ret_profit_take': 'float64',
                'barrier': 'object',
                'ret_barrier': 'float64',
            }
        )
        events = dd.concat([events, ee], axis='columns')
    elif isinstance(events, pd.DataFrame):
        ee = events.apply(
            get_barrier_hit,
            args=(x,),
            axis='columns',
            result_type='expand',
            raw=False
        )
        events = pd.concat([events, ee], axis='columns')
    else:
        raise RuntimeError('events parameter must be pd.DataFrame or dd.DataFrame')

    return events


def get_thresholded_events(
        df: Union[pd.DataFrame, dd.DataFrame],
        metric_threshold: float,
        event_col: str,
        horizon: timedelta = None,
        metric: Callable = compute_return,
        metric_name: str = "Return",
        metric_abs: bool = True
    ) -> Union[pd.DataFrame, dd.DataFrame]:
    """
    Symmetric CUSUM Filter [Lopez de Prado 2.5.2.1] applied to irregular time series.
    Lower level function that finds absolute returns over a horizon that are
    above a threshold
    :param df: Pandas/Dask Series of prices, indexed by DatetimeIndex
    :param metric_threshold: threshold
    :param event_col: which column to use for return computation
    :param horizon: timedelta indicating return horizon
    :param metric: function that takes DataFrame, str, timedelta and returns DataFrame
    :param metric_name:
    :param metric_abs:
    :return: Pandas DataFrame where index is end time of return and values are return and
    start time of return
    """
    metric(df, event_col, horizon)
    if metric_abs:
        d_filter = df[f'{metric_name}_{event_col}'].abs() > metric_threshold
    else:
        d_filter = df[f'{metric_name}_{event_col}'] > metric_threshold
    d = df[d_filter]
    d[f'{metric_name}_event'] = d.index
    d = d.set_index('t0')
    return d[[f'{metric_name}_{event_col}', f'{metric_name}_event']]