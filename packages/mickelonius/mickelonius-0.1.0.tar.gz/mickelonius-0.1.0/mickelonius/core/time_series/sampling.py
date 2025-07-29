import numpy as np
import pandas as pd


def get_num_co_events(close_index, t1, molecule):
    """
    Section 4.3, Lopez de Prado, Adv. in Financial Mach. Learning
    Compute the number of concurrent events per bar.
    Any event that starts before t1[molecule].max() impacts the count.
    :param close_index: Pandas DatetimeIndex of time_series days
    :param t1: Pandas Series of event start (DatetimeIndex) and stop (values) times
    :param molecule: Pandas DatetimeIndex
        +molecule[0] is the date of the first event on which the weight will be computed
        +molecule[-1] is the date of the last event on which the weight will be computed
    :return: Pandas Series where
        DatetimeIndex contains event start times and
        values are number of overlaps
    """
    # 1) find events that span the period [molecule[0], molecule[-1]]
    t1 = t1.fillna(close_index[-1])     # unclosed events still must impact other weights
    t1 = t1[t1 >= molecule[0]]          # events that end at or after molecule[0]
    t1 = t1.loc[:t1[molecule].max()]    # events that start at or before t1[molecule].max()

    # 2) count events spanning a bar
    iloc = close_index.searchsorted(np.array([t1.index[0], t1.max()]))
    count = pd.Series(0, index=close_index[iloc[0]:iloc[1] + 1])
    for t_in, t_out in t1.items():
        count.loc[t_in:t_out] += 1.

    return count.loc[molecule[0]:t1[molecule].max()]


def get_sample_tw(t1, num_co_events, molecule):
    """
    Section 4.4 Lopez de Prado
    Compute average uniqueness over event's lifetime
    :param t1: Pandas DataFrameSeries of event start (DatetimeIndex) and stop (values) times
    :param num_co_events: Pandas Series where DatetimeIndex contains event start times and values are number of overlaps
    :param molecule: Pandas DatetimeIndex
        +molecule[0] is the date of the first event on which the weight will be computed
        +molecule[-1] is the date of the last event on which the weight will be computed
    :return: Pandas Series where
        DatetimeIndex contains event start times and
        values are average uniquenesses
    """
    # Derive average uniqueness over the event's lifespan
    wght = pd.Series(index=molecule)
    for t_in, t_out in t1.loc[wght.index].items():
        wght.loc[t_in] = (1. / num_co_events.loc[t_in:t_out]).mean()
    return wght


def get_indicator_matrix(bar_index, event_ranges):
    """
    Section 4.5 Lopez de Prado, Snippet 4.3
    :param bar_index: Pandas Index
    :param event_ranges: Pandas Dataframe/Series with index = start time/idx, value = end time/idx
    :return:
    """
    err_msg = (f"dtypes of bar_index and event_ranges.index need to match: "
               f"bar_index.dtype={bar_index.dtype}, "
               f"event_ranges.index.dtype={event_ranges.index.dtype}")
    assert pd.api.types.is_dtype_equal(bar_index.dtype, event_ranges.index.dtype), err_msg

    indicator_matrix = pd.DataFrame(0, index=bar_index, columns=bar_index)  # shape[0]))
    for i, (t0, t1) in enumerate(event_ranges.items()):
        indicator_matrix.loc[t0, t0:t1] = 1.
    return indicator_matrix


def get_avg_uniqueness(ind_matrix):
    """
    Section 4.5 Lopez de Prado, snippet 4.4
    :param ind_matrix:
    :return:
    """
    # Average uniqueness from indicator matrix
    c = ind_matrix.sum(axis=1) # concurrency
    u = ind_matrix.div(c, axis=0).fillna(0) # uniqueness
    avg_u = u[u>=0].mean() # average uniqueness
    return avg_u


def seq_bootstrap(ind_matrix, s_length = None):
    """
    Section 4.5 Lopez de Prado
    :param ind_matrix:
    :param s_length:
    :return:
    """
    # Generate a sample via sequential bootstrap
    if s_length is None:
        s_length = ind_matrix.shape[1]
    phi = []
    while len(phi) < s_length:
        avg_u = pd.Series(dtype=np.float64)
        for i in ind_matrix:
            ind_matrix_ = ind_matrix[phi + [i]]  # reduce indM
            avg_u.loc[i] = get_avg_uniqueness(ind_matrix_).iloc[-1]
        prob = avg_u/avg_u.sum()  # draw prob
        phi += [np.random.choice(ind_matrix.columns, p=prob)]
    return phi


def sample_w_ret(t1, num_co_events, close, molecule):
    """
    Section 4.6 Lopez de Prado, Derive sample weight by return attribution
    :param t1:
    :param num_co_events:
    :param close:
    :param molecule:
    :return:
    """
    ret = np.log(close).diff()  # log-returns, so that they are additive
    wght = pd.Series(index=molecule)
    for t_in, t_out in t1.loc[wght.index].items():
        wt = (ret.loc[t_in:t_out] / num_co_events.loc[t_in:t_out]).replace(np.inf, 0).replace(-np.inf, 0).sum()
        wght.loc[t_in] = wt
    return wght.abs()


def get_time_decay(uniqueness, c=1.):
    """
    Section 4.7 Lopez de Prado, time-decay
    Apply piecewise-linear decay to observed uniqueness
    Newest observation gets d=1, oldest observation gets d=max(0,c)
    Note that decay takes place according to cumulative uniqueness, because a chronological
    decay would reduce weights too fast in the presence of redundant observations
    :param uniqueness: Pandas Series
    :param c: weight of earliest sample (in terms of avg uniqueness), c=0 for x<=-cT,
              where 1:T is the integer index of the uniqueness time series
    :return:
    """

    # cumulative avg uniqueness
    sigma_u = uniqueness.sort_index().cumsum()

    # compute slope
    if c >= 0:
        b = (1. - c) / sigma_u.iloc[-1]
    else:
        b = 1./((c + 1) * sigma_u.iloc[-1])

    # intercept
    a = 1. - b*sigma_u.iloc[-1]

    # weights
    d = a + b*sigma_u

    # clip weights to 0 when c < 0
    d[d<0] = 0

    return d
