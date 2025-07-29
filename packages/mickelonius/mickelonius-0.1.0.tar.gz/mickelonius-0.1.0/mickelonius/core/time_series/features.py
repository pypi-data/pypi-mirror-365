from dask import dataframe as dd
from typing import Union, List, Tuple, Callable, Optional
from datetime import timedelta, datetime

import pandas as pd
import numpy as np



def get_daily_vol(x, col: str = 'Close', horizon: int = 30, lookback: int = 100):
    """
    Use exponential moving average of daily returns to compute volatility
    as time series.
    :param x: Pandas Dataframe that contains field named by "col" parameter
    :param col: field used for price data
    :param horizon: volatility horizon in days
    :param lookback: Exponential Mov Avg lookback
    :return: Pandas Series with DatetimeIndex as in x, and values of estimated vol
    """
    d = np.log(x[col]).diff().dropna()
    return np.sqrt(horizon)*d.ewm(span=lookback).std()


def compute_raw_delta_t(
    x: Union[pd.DataFrame, dd.DataFrame],
    col: str = 'Close'
):
    """
    Compute time deltas of a time series, with accommodation
    of irregular sampling
    :param x: Pandas/Dask Dataframe that contains field named by "col" parameter,
              with a DatetimeIndex
    :param col: field used for price data
    :return: Pandas Series with DatetimeIndex as in x, and value = current timestamp minus
             the previous timestamp
    """
    # if isinstance(x, pd.DataFrame):
    #     x['t'] = x.index
    #     x['delta_t'] = x['t'].diff(1).fillna(timedelta(0))
    #     # x.iloc[0]['delta_t'] = 0
    #     x[f'delta_{col}'] = x[col].diff(1).fillna(0)
    #     # x.iloc[0][f'delta_{col}'] = 0
    #
    # elif isinstance(x, dd.DataFrame):
    x['t'] = x.index
    x['delta_t'] = x['t'].diff(1).fillna(timedelta(0))
    x[f'delta_{col}'] = x[col].diff(1).fillna(0)


def compute_expm(
    x: Union[pd.DataFrame, dd.DataFrame],
    tau: float,
    col: str = 'Close',
    append_aux_fields: bool = False
):
    """
    Compute exponential moving average of a time series, with accommodation
    of irregular sampling
    :param x: Pandas Dataframe that contains field named by "col" parameter,
              with a DatetimeIndex
    :param tau: time constant of exponential mov avg
    :param col: field used for price data
    :param append_aux_fields: keep t, delta_t fields used to construct
    :return: Pandas Series with DatetimeIndex as in x, and value = current timestamp minus
             the previous timestamp
    """
    x = compute_raw_delta_t(x, col)
    mu = np.exp(-x['delta_t']/tau)
    ema_col = f'EMA_{col}'
    x[ema_col] = mu*x[ema_col].shift(1) + (1-mu)*x[col]

    if not append_aux_fields:
        x = x.drop(['t', 'delta_t', f'delta_{col}'])

    return x


def compute_return(df: Union[pd.DataFrame, dd.DataFrame],
                   price_column: str = 'Close',
                   horizon: timedelta = None,
                   append_aux_fields: bool = False,
                   use_log: bool = True) -> Union[pd.DataFrame, dd.DataFrame]:
    """
    Compute simple returns of a time series, with accommodation
    of irregular sampling
    :param x: Pandas/Dask Dataframe that contains field named by "col" parameter,
              with a DatetimeIndex
    :param price_column: field used for price data
    :param horizon: how far forward to compute return
    :param append_aux_fields: keep delta_{col}, delta_t fields used to construct returns
    :param use_log:
    :return: Pandas DataFrame with DatetimeIndex as start time of return and
             Return_{price_column} = return
             {price_column} = price
             t = end time of return
    """
    compute_raw_delta_t(df, price_column)
    ret_col = f'Return_{price_column}'
    delta_col = f'delta_{price_column}'

    if horizon is None:
        if use_log:
            df[ret_col] = np.log(df[price_column]) - np.log(df[price_column].shift(1))
        else:
            df[ret_col] = df[delta_col] / df[price_column].shift(1) - 1.0

        df['t0'] = df['t'].shift(1).fillna(datetime.fromtimestamp(0))
        df['t0'] = df['t0'].astype('datetime64[ns]')

    else:
        if isinstance(df, pd.DataFrame):
            if use_log:
                df[ret_col] = df[price_column].rolling(horizon).apply(lambda x: np.log(x.iloc[-1]) - np.log(x.iloc[0]))
            else:
                df[ret_col] = df[price_column].rolling(horizon).apply(lambda x: (x.iloc[-1] - x.iloc[0]) / x.iloc[0])
            df['t0'] = df['t'].astype(int).rolling(horizon).apply(lambda x: x.iloc[0])
            df['t0'] = df['t0'].astype('datetime64[ns]')
            if append_aux_fields:
                df['x[-1]'] = df[price_column].rolling(horizon).apply(lambda x: x.iloc[-1])
                df['x[0]'] = df[price_column].rolling(horizon).apply(lambda x: x.iloc[0])

        elif isinstance(df, dd.DataFrame):
            if use_log:
                df[ret_col] = df[price_column].rolling(horizon).apply(lambda x: np.log(x.iloc[-1]) - np.log(x.iloc[0]), raw=False)
            else:
                df[ret_col] = df[price_column].rolling(horizon).apply(lambda x: (x.iloc[-1] - x.iloc[0]) / x.iloc[0], raw=False)
            df['t0'] = df['t'].astype(int).rolling(horizon).apply(lambda x: x.iloc[0], raw=False).astype('datetime64[ns]')
            df['t0'] = df['t0'].astype('datetime64[ns]')
            if append_aux_fields:
                df['x[-1]'] = df[price_column].rolling(horizon).apply(lambda x: x.iloc[-1], raw=False)
                df['x[0]'] = df[price_column].rolling(horizon).apply(lambda x: x.iloc[0], raw=False)
        else:
            raise RuntimeError('t_events parameter must be pandas.DataFrame or dask.dataframe.DataFrame')
    if not append_aux_fields:
        df = df.drop(['delta_t', delta_col], axis=1)


def get_vol(x: Union[pd.DataFrame, dd.DataFrame],
            horizon: timedelta,
            col: str):
    """
    Use short-term returns to compute volatility as time series.
    :param x: Pandas Dataframe that contains field named by "col" parameter
    :param col: field used for price data
    :param horizon: volatility horizon as timedelta
    :return: Pandas Series with DatetimeIndex as in x, and values of estimated vol
    """
    rets = compute_return(x, col, horizon)
    return rets[f'Return_{col}'].dropna().rolling(horizon).std()
