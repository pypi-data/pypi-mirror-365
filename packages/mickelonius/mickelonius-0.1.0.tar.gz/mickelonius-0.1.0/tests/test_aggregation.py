import pandas as pd
import polars as pl
import pyspark.pandas as ps
from mickelonius.core.time_series.aggregations import tick_bars
from tests import test_data_path


def test_tick_bars_pandas(tick_df_pandas):
    tick_bar_df = tick_bars(tick_df_pandas, 100, 'Price', 'Size')

    assert tick_bar_df.shape == (100, 7)


def test_tick_bars_polars(tick_df_pandas):
    test_df = pl.DataFrame(tick_df_pandas)
    tick_bar_df = tick_bars(test_df, 100, 'Price', 'Size')

    assert tick_bar_df.shape == (100, 7)


def test_tick_bars_pyspark(spark, tick_df_pandas):
    # test_df = ps.from_pandas(test_df)
    test_df = spark.createDataFrame(tick_df_pandas)
    tick_bar_df = tick_bars(test_df, 100, 'Price', 'Size')

    assert (tick_bar_df.count(), len(tick_bar_df.columns)) == (100, 7)
