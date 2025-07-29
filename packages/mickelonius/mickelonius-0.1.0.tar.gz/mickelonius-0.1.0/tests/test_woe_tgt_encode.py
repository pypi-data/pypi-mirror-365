import pytest

from mickelonius.core.feature_engineering.woe import (
    target_encode,
    add_target_encode_woe,
    woe_iv,
)

test_k_pct = 0.01
test_f = 100.0


def test_simple_encode_pandas(simple_encode_test_df_pandas):
    test_features = ['Feature1']
    response_col = 'Outcome'
    df = target_encode(simple_encode_test_df_pandas, test_features, response_col, test_k_pct, test_f)

    expected_col = f"LOOEncode_{'_'.join(test_features)}_{response_col}"
    expected_ema_col = f"EMA_LOOEncode_{'_'.join(test_features)}_{response_col}"
    assert expected_col in df.columns
    assert df[expected_col].equals(simple_encode_test_df_pandas['LOOEncode'])
    assert expected_ema_col in df.columns
    assert df[expected_ema_col].equals(simple_encode_test_df_pandas['EMA_LOOEncode'])


def test_multi_encode_pandas(multi_encode_test_df_pandas):
    test_features = ['Feature1', 'Feature2']
    response_col = 'Outcome'
    df = target_encode(multi_encode_test_df_pandas, test_features, response_col, test_k_pct, test_f)

    expected_col = f"LOOEncode_{'_'.join(test_features)}_{response_col}"
    expected_ema_col = f"EMA_LOOEncode_{'_'.join(test_features)}_{response_col}"
    assert expected_col in df.columns
    assert df[expected_col].equals(multi_encode_test_df_pandas['LOOEncode'])
    assert expected_ema_col in df.columns
    assert df[expected_ema_col].equals(multi_encode_test_df_pandas['EMA_LOOEncode'])


def test_simple_encode_dask(simple_encode_test_df_dask):
    test_features = ['Feature1']
    response_col = 'Outcome'
    df = target_encode(simple_encode_test_df_dask, test_features, response_col, test_k_pct, test_f)
    df = df.compute()

    df0 = simple_encode_test_df_dask.compute()
    expected_col = f"LOOEncode_{'_'.join(test_features)}_{response_col}"
    expected_ema_col = f"EMA_LOOEncode_{'_'.join(test_features)}_{response_col}"
    assert expected_col in df.columns
    assert df[expected_col].equals(df0['LOOEncode'])
    assert expected_ema_col in df.columns
    assert df[expected_ema_col].equals(df0['EMA_LOOEncode'])


def test_multi_encode_dask(multi_encode_test_df_dask):
    test_features = ['Feature1', 'Feature2']
    response_col = 'Outcome'
    df = target_encode(multi_encode_test_df_dask, test_features, response_col, test_k_pct, test_f)
    df = df.compute().sort_values(['Feature1', 'Feature2'])

    df0 = multi_encode_test_df_dask.compute().sort_values(['Feature1', 'Feature2'])
    expected_col = f"LOOEncode_{'_'.join(test_features)}_{response_col}"
    expected_ema_col = f"EMA_LOOEncode_{'_'.join(test_features)}_{response_col}"
    assert expected_col in df.columns
    assert df[expected_col].equals(df0['LOOEncode'])
    assert expected_ema_col in df.columns
    assert df[expected_ema_col].equals(df0['EMA_LOOEncode'])


def test_add_target_encode_woe(simple_encode_test_df_pandas):
    df = simple_encode_test_df_pandas
    df_ = add_target_encode_woe(
        df,
        cols=['Feature1'],
        response_col='Outcome'
    )
    print('')


def _check_simple_encode_woe(df_woe_iv):
    assert pytest.approx(df_woe_iv["iv"], rel=1e-2) == 0.038
    assert pytest.approx(df_woe_iv["woe"]["A"], rel=1e-2) == 0.405
    assert pytest.approx(df_woe_iv["woe"]["B"], rel=1e-2) == 0.741
    assert pytest.approx(df_woe_iv["woe"]["C"], rel=1e-2) == -0.356


def test_woe_iv_simple(simple_encode_test_df_pandas):
    df = simple_encode_test_df_pandas
    df_woe_iv = woe_iv(
        df,
        feature_cols=['Feature1'],
        response_col='Outcome'
    )
    _check_simple_encode_woe(df_woe_iv)


def test_woe_iv_simple_dask(simple_encode_test_df_dask):
    df = simple_encode_test_df_dask
    df_woe_iv = woe_iv(
        df,
        feature_cols=['Feature1'],
        response_col='Outcome'
    )
    _check_simple_encode_woe(df_woe_iv)


def _check_multi_encode_woe(df_woe_iv):
    assert pytest.approx(df_woe_iv["iv"], rel=1e-2) == 0.339
    assert pytest.approx(df_woe_iv["woe"][("A", "X")], rel=1e-2) == 0.074
    assert pytest.approx(df_woe_iv["woe"][("A", "Y")], rel=1e-2) == -0.436
    assert pytest.approx(df_woe_iv["woe"][("A", "Z")], rel=1e-2) == -1.0245
    assert pytest.approx(df_woe_iv["woe"][("B", "X")], rel=1e-2) == 0.661
    assert pytest.approx(df_woe_iv["woe"][("B", "Y")], rel=1e-2) == 0.074
    assert pytest.approx(df_woe_iv["woe"][("B", "Z")], rel=1e-2) == 0.584
    assert pytest.approx(df_woe_iv["woe"][("C", "X")], rel=1e-2) == 1.683
    assert pytest.approx(df_woe_iv["woe"][("C", "Y")], rel=1e-2) == -1.225


def test_woe_iv_multi(multi_encode_test_df_pandas):  # , woe_iv_multi):
    df = multi_encode_test_df_pandas
    df_woe_iv = woe_iv(
        df,
        feature_cols=['Feature1', 'Feature2'],
        response_col='Outcome'
    )
    _check_multi_encode_woe(df_woe_iv)


def test_woe_iv_multi_dask(multi_encode_test_df_dask):
    df = multi_encode_test_df_dask
    df_woe_iv = woe_iv(
        df,
        feature_cols=['Feature1', 'Feature2'],
        response_col='Outcome'
    )
    _check_multi_encode_woe(df_woe_iv)
