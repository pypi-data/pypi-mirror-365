from typing import Union, Iterable, Optional, List, Dict, Any
import dask.dataframe as dd
import pandas as pd
import numpy as np
import string
import random
import math
import functools

np.random.seed(10)
random.seed(10)


def add_target_encode_woe(
    df: Union[pd.DataFrame, dd.DataFrame],
    cols: List[str],
    response_col: str,
    k_pct: Optional[float] = 0.01,
    f: Optional[float] = 100.0,
    append_cols: Optional[bool] = True,
    df_test: Optional[Union[pd.DataFrame, dd.DataFrame]] = None
) -> Dict[str, Dict[str, List[Any] | int]]:
    '''
    Appends WoE_<original column name>,
            IV_<original column name>,
            LOOEncode_<original column name>,
            EMA_LOOEncode_<original column name>

    for each column name specified in input params.  There is a weighted average function

        lambda(n) * mean(dataset[level, response]) + (1- lambda(n)) * mean(dataset[response])

    where

        N = Total number of records
        n = Number of records for category
        k = k_pct * N
        lambda(n) = 1 / [1 + exp(-(n-k)/f)] and

    that determines how to blend the overall and category response means.

    :param df: Input data frame
    :param cols: Column names to compute WoE, IV on
    :param response_col: Column name that contains binary response
    :param k_pct: lower/higher value determines inflection point in weighted avg fc'n
                  and fewer/greter number of samples required for a given category
    :param f: lower/higher value more/less steepness in weighted avg fc'n
    :param append_cols: enable appending WoE and IV columns to input data frame
    :param df_test: test data frame to use WoE, IV computed from input data frame
    :return: {
        '<column name>': {
            'woe' list of (column name, WoE value) tuples ,sorted by WoE,
            'iv': Information Value
        }
    }
    '''
    n = df.shape[0]

    # number of events and non-events
    evt_cts = df.groupby([response_col]).size()

    if df_test is not None:
        n_test = df_test.shape[0]

    woe_iv = {}
    for col in cols:
        woe_iv[col] = {
            'woe': [],
            'iv': 0,
        }

        # number of events and non-events for each category
        evt_cat_cts = df.groupby([col, response_col]).size()

        # number of each category
        cat_cts = df.groupby([col]).size()

        p = df[response_col].mean()
        k = k_pct * n

        if append_cols:
            df['WoE_%s' % col] = pd.Series(np.nan * n, index=df.index)
            df['IV_%s' % col] = pd.Series(np.nan * n, index=df.index)
            df['LOOEncode_%s' % col] = pd.Series(np.nan * n, index=df.index)
            df['EMA_LOOEncode_%s' % col] = pd.Series(np.nan * n, index=df.index)
            if df_test is not None:
                df_test['WoE_%s' % col] = pd.Series(np.nan * n_test, index=df_test.index)
                df_test['IV_%s' % col] = pd.Series(np.nan * n_test, index=df_test.index)
                df_test['LOOEncode_%s' % col] = pd.Series(np.nan * n_test, index=df_test.index)
                df_test['EMA_LOOEncode_%s' % col] = pd.Series(np.nan * n_test, index=df_test.index)

        actual_cat_values = df[col].unique().tolist()
        for c in actual_cat_values:
            if (df[col].dtype == np.float64 and not np.isnan(c)) or \
                    df[col].dtype != np.float64:

                # group 1, event
                try:
                    x = evt_cat_cts[c, 1]
                except:
                    x = 0
                evt_pct = (x + 0.5) / evt_cts[1]

                # group 0, non-event
                try:
                    x = evt_cat_cts[c, 0]
                except:
                    x = 0
                non_evt_pct = (x + 0.5) / evt_cts[0]

                # WoE = log{ [(N in group 0 + 0.5)/N_0] / [(N in group 1 + 0.5)/N_1] } ~ log[(%grp of 0)/(%grp of 1)]
                woe = math.log(non_evt_pct / evt_pct)
                if append_cols:
                    df.loc[df[col] == c, 'WoE_%s' % col] = woe
                    if df_test is not None:
                        df_test.loc[df[col] == c, 'WoE_%s' % col] = woe
                woe_iv[col]['woe'].append((c, woe))

                iv = (non_evt_pct - evt_pct) * woe
                if append_cols:
                    df.loc[df[col] == c, 'IV_%s' % col] = iv
                    if df_test is not None:
                        df_test.loc[df_test[col] == c, 'IV_%s' % col] = iv
                woe_iv[col]['iv'] += iv

                if append_cols:
                    if cat_cts[c] > 1:
                        loo = (float(cat_cts[c]) + (df.loc[df[col] == c, response_col] - 1).sum()) / (cat_cts[c] - 1)
                    else:
                        loo = df.loc[df[response_col] == c, response_col]
                    df.loc[df[col] == c, 'LOOEncode_%s' % col] = loo
                    if df_test is not None:
                        df_test.loc[df_test[col] == c, 'LOOEncode_%s' % col] = loo

                    l = 1 / (1 + math.exp(-(cat_cts[c] - k) / f))
                    df.loc[df[col] == c, 'EMA_LOOEncode_%s' % col] = l * loo + (1 - l) * p
                    if df_test is not None:
                        df_test.loc[df_test[col] == c, 'EMA_LOOEncode_%s' % col] = l * loo + (1 - l) * p

        woe_iv[col]['woe'].sort(key=lambda x: x[1])

    return woe_iv


def make_test_df():
    n = 20

    nc = 3
    cat_values = list(string.ascii_lowercase)[:nc]
    cats = [random.choice(cat_values) for i in range(n)]

    nk = 3
    ord_values = range(nk)
    ords = [random.choice(ord_values) for i in range(n)]

    nrng = [-0.5, 0.5]
    nums = np.random.uniform(nrng[0], nrng[1], n)

    nbins = 10
    binsz = (nrng[1]-nrng[0])/nbins
    bins = np.digitize(nums, [nrng[0] + binsz*i for i in range(20)])

    p = 0.5
    resp = np.random.binomial(1, p, n)

    df = pd.DataFrame({
        'idx': range(n),
        'cat': cats,
        'ord': ords,
        'num': nums,
        'response': resp
    })
    df.set_index('idx')

    cat_dtype = pd.api.types.CategoricalDtype(categories=cat_values, ordered=True)
    df.cat.astype(cat_dtype)

    return df


def woe_iv(df: Union[pd.DataFrame, dd.DataFrame],
           feature_cols:  Union[str, List[str]],
           response_col: str) -> Dict:
    """
    Compute weight-of-evidence (WoE) and Information Value for combination of
    feature_cols.
    :param df:
    :param feature_cols: list of feature column names
    :param response_col: name of response column, should be discrete and finite cardinality
    i.e. 1 of N classes or bins, if columns are numerical, it is advised to bin the data
    and use the bins as an N-class category
    :return: original data frame with WoE and IV columns appended
    """
    composite_col = '_'.join([f for f in feature_cols])

    # from itertools import product
    # uniques = [df[i].unique().tolist() for i in feature_cols]
    # unique_tuples = pd.DataFrame(product(*uniques), columns=feature_cols)

    # Create tuple column of multiple specified features
    if isinstance(feature_cols, list):
        if len(feature_cols) > 1:
            df[composite_col] = df[feature_cols].apply(tuple, axis=1)
        elif len(feature_cols) == 1:
            df[composite_col] = df[feature_cols[0]]
        else:
            raise RuntimeError('feature_cols must have at least one element if it\'s a list')
    elif isinstance(feature_cols, str):
        df[composite_col] = df[feature_cols]

    # number of each category
    if isinstance(df, pd.DataFrame):
        cat_cts = df.groupby(composite_col).size().to_dict()
        evt_cat_cts = df.groupby([composite_col, response_col]).size()
        evt_cts = df.groupby(response_col).size().to_dict()
    elif isinstance(df, dd.DataFrame):
        cat_cts = df.groupby(composite_col).size().compute().to_dict()
        evt_cat_cts = df.groupby([composite_col, response_col]).size().compute()
        evt_cts = df.groupby(response_col).size().compute().to_dict()
    else:
        raise RuntimeError('Input dataframe must be either dask.distributed.DataFrame or pandas.DataFrame')

    woe_iv = {
        'iv': 0,
        'woe': {},
    }
    for cat, ct in cat_cts.items():
        #TODO: accomodate more than one category for WoE, IV computations
        #TODO: accomodate continuous response

        # group 1, event
        try:
            x = evt_cat_cts[cat, 1]
        except:
            x = 0
        evt_pct = (x + 0.5) / evt_cts[1]

        # group 0, non-event
        try:
            x = evt_cat_cts[cat, 0]
        except:
            x = 0
        non_evt_pct = (x + 0.5) / evt_cts[0]

        # WoE = log{ [(N in group 0 + 0.5)/N_0] / [(N in group 1 + 0.5)/N_1] } ~ log[(%grp of 0)/(%grp of 1)]
        woe = math.log(non_evt_pct / evt_pct)
        woe_iv['iv'] = (non_evt_pct - evt_pct) * woe
        woe_iv['woe'][cat] = woe

    return woe_iv  # sorted(woe_iv, key=lambda x: x[2], reverse=True)


def target_encode(
    df: Union[pd.DataFrame, dd.DataFrame],
    feature_cols: Iterable[str],
    response_col: str,
    k_pct: Optional[float] = 0.01,
    f: Optional[float] = 100.0
) -> Union[pd.DataFrame, dd.DataFrame]:
    """
    Append Leave-One-Out (LOO) target encoded feature to input dataframe. k_pct and
    f are parameters to exponential weighting of category-specific and sample mean
    of response.
    :param df: Pandas or Dask dataframe that contains feature_cols and response_col
    :param feature_cols: Features to target encode. For more than one feature, combinations
    of the values of the feature_cols become the composite feature to target encode
    :param response_col: Should be binary (for now)
    :param k_pct: percentage of total sample required to weight category and sample
    means evenly, i.e. 0.5, or an inflection point of the exponential weighting function
    :param f: Modulates steepness of exponential weighting function. 0 = step function
    :return:
    """
    if isinstance(df, dd.DataFrame):
        return target_encode_dask(df, feature_cols, response_col, k_pct, f)
    else:
        response_sample_mean = df[response_col].mean()
        sample_ct_by_category = df.groupby(feature_cols).count()[response_col].to_dict()

        k = k_pct * sum(sample_ct_by_category.values())
        target_encode_col = f"LOOEncode_{'_'.join(feature_cols)}_{response_col}"
        df[target_encode_col] = 0
        ema_target_encode_col = f"EMA_LOOEncode_{'_'.join(feature_cols)}_{response_col}"
        df[target_encode_col] = 0

        for cat, ct in sample_ct_by_category.items():
            if isinstance(cat, tuple):
                filter_condition = (df[feature_cols[0]] == cat[0])
                for i, sub_cat in enumerate(cat[1:]):
                    filter_condition = filter_condition * (df[feature_cols[i+1]] == cat[i+1])
            else:
                filter_condition = df[feature_cols[0]] == cat

            if ct > 1:
                response_sum = df.loc[filter_condition, response_col].sum()
                loo = (response_sum - df.loc[filter_condition, response_col]) / (ct - 1)
                l = 1 / (1 + math.exp(-(ct - k) / f))
                ema_loo = l * loo + (1 - l) * response_sample_mean
            elif ct == 1:
                loo = df.loc[filter_condition, response_col]
                ema_loo = df.loc[filter_condition, response_col]
            elif ct < 1:
                loo = 0.5
                ema_loo = 0.5

            df.loc[filter_condition, target_encode_col] = loo
            df.loc[filter_condition, ema_target_encode_col] = ema_loo

            # l = 1 / (1 + math.exp(-(cat_cts[cat] - k) / f))
            # df.loc[df[feature_cols] == cat, f"EMA_LOOEncode_{'_'.join(feature_cols)}_{response_col}"] = l * loo + (1 - l) * p

    return df


def compute_loo(x, response_sum, response_col, sample_ct):
    return (response_sum - x[response_col]) / (sample_ct - 1)


def compute_ema_loo(x, sample_ct, k: float, f: float, loo_col: str, p: float):
    l = 1 / (1 + math.exp(-(sample_ct - k) / f))
    return l * x[loo_col] + (1 - l) * p


def target_encode_dask(df: dd.DataFrame,
                       feature_cols: Iterable[str],
                       response_col: str,
                       k_pct: float=0.01,
                       f: float=100.0
                       ) -> dd.DataFrame:
    """
    Append Leave-One-Out (LOO) target encoded feature to input dataframe. k_pct and
    f are parameters to exponential weighting of category-specific and sample mean
    of response.
    :param df: Pandas or Dask dataframe that contains feature_cols and response_col
    :param feature_cols: Features to target encode. For more than one feature, combinations
    of the values of the feature_cols become the composite feature to target encode
    :param response_col: Should be binary (for now)
    :param k_pct: percentage of total sample required to weight category and sample
    means evenly, i.e. 0.5, or an inflection point of the exponential weighting function
    :param f: Modulates steepness of exponential weighting function. 0 = step function
    :return:
    """
    response_sample_mean = df[response_col].mean().compute()
    sample_ct_by_category = df.groupby(feature_cols).count()[response_col].compute().to_dict()
    k = k_pct * sum(sample_ct_by_category.values())
    loo_col = f"LOOEncode_{'_'.join(feature_cols)}_{response_col}"
    ema_loo_col = f"EMA_LOOEncode_{'_'.join(feature_cols)}_{response_col}"

    df_ = None
    for cat, sample_ct in sample_ct_by_category.items():
        if isinstance(cat, tuple):
            filter_condition = (df[feature_cols[0]] == cat[0])
            for i, sub_cat in enumerate(cat[1:]):
                filter_condition = filter_condition & (df[feature_cols[i+1]] == cat[i+1])
        else:
            filter_condition = df[feature_cols[0]] == cat

        if sample_ct > 1:
            response_sum = df.loc[filter_condition, response_col].sum().compute()

            # Want to be able to send local params to workers
            loo_fcn = functools.partial(compute_loo, **{
                'response_sum': response_sum,
                'response_col': response_col,
                'sample_ct': sample_ct_by_category[cat],
            })
            ema_loo_fcn = functools.partial(compute_ema_loo, **{
                'k': k,
                'f': f,
                'sample_ct': sample_ct_by_category[cat],
                'loo_col': loo_col,
                'p': response_sample_mean,
            })

            if df_ is None:
                df_ = df.loc[filter_condition].assign(**{loo_col: loo_fcn}) \
                                              .assign(**{ema_loo_col: ema_loo_fcn})
            else:
                df_ = dd.concat([df_, df.loc[filter_condition].assign(**{loo_col: loo_fcn})
                                                                    .assign(**{ema_loo_col: ema_loo_fcn})])
        elif sample_ct == 1:
            if df_ is None:
                df_ = df.loc[filter_condition].assign(**{loo_col: df.loc[filter_condition][response_col]}) \
                                              .assign(**{ema_loo_col: df.loc[filter_condition][response_col]})
            else:
                df_ = dd.concat([df_, df.loc[filter_condition]
                                               .assign(**{loo_col: df.loc[filter_condition][response_col]})
                                               .assign(**{ema_loo_col: df.loc[filter_condition][response_col]})
                                      ])
        elif sample_ct < 1:
            if df_ is None:
                df_ = df.loc[filter_condition]
                df_.assign(**{loo_col: 0.5}).assign(**{ema_loo_col: 0.5})
            else:
                df_ = dd.multi.concat([df_, df.loc[filter_condition].assign(**{loo_col: 0.5})]).assign(**{ema_loo_col: 0.5})

        # l = 1 / (1 + math.exp(-(cat_cts[cat] - k) / f))
        # df.loc[df[feature_cols] == cat, f"EMA_LOOEncode_{'_'.join(feature_cols)}_{response_col}"] = l * loo + (1 - l) * p

    return df_


if __name__ == '__main__':
    df = make_test_df()
    add_target_encode_woe(df, ['cat'], 'response', k_pct=0.01, f=10)
    print(df)
    print(df.dtypes)

    #df[(df.response==1) & (df.cat=='a')]
















