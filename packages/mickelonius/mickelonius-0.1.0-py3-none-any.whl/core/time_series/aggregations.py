# TODO: implement runs bars
# TODO: implement one function for tick, volume, dollar bars
import pandas as pd
import polars as pl
from dask import dataframe as dd
from pyspark.sql import DataFrame as SparkDataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window
# from pyspark.pandas.frame import DataFrame as SparkAPIDataFrame

def tick_bars(df, tick_threshold, price_column, volume_column):
    """
    compute tick bars
    :param df: Pandas DataFrame with DatetimeIndex
    :param price_column: str
    :param tick_threshold: int, threshold value for ticks
    :param volume_column: [optional], str, column to compute volume
    :return: DataFrame with columns t(index), Open, High, Low, Close,
             Bid, Ask, Volume(Optional, must specify volume_column)
    """

    if type(df) in [pd.DataFrame]:
        df.reset_index(inplace=True)
        df['seq'] = df.index % tick_threshold
        df['Low'] = df[price_column].rolling(tick_threshold).min()
        df['High'] = df[price_column].rolling(tick_threshold).max()
        df['Close'] = df[price_column].rolling(tick_threshold).apply(lambda df: df.iloc[-1])
        df['Open'] = df[price_column].rolling(tick_threshold).apply(lambda df: df.iloc[0])
        df['Volume'] = df[volume_column].rolling(tick_threshold).sum()

        sampled_df = df[df['seq'] == tick_threshold-1]
        sampled_df = sampled_df.drop(['seq', price_column, volume_column], axis=1)
        sampled_df.set_index('t', inplace=True)
        return sampled_df

    elif type(df) == pl.DataFrame:
        df = df.with_columns((pl.arange(0, df.height) % tick_threshold).alias('seq'))
        df = df.with_columns([
            df[price_column].rolling_min(window_size=tick_threshold).alias('Low'),
            df[price_column].rolling_max(window_size=tick_threshold).alias('High'),
            df[price_column].rolling_map(lambda x: x[-1], window_size=tick_threshold).alias('Close'),
            df[price_column].rolling_map(lambda x: x[0], window_size=tick_threshold).alias('Open'),
        ])
        df = df.with_columns(df[volume_column].rolling_sum(window_size=tick_threshold).alias('Volume'))
        df = df.drop([price_column, volume_column])
        return df.filter(pl.col('seq') == tick_threshold - 1).drop('seq')

    elif type(df) == dd.DataFrame:
        df = df.reset_index()
        df['seq'] = df.index % tick_threshold
        df['Low'] = df[price_column].rolling(tick_threshold).min()
        df['High'] = df[price_column].rolling(tick_threshold).max()
        df['Close'] = df[price_column].rolling(tick_threshold).apply(lambda x: x.iloc[-1])
        df['Open'] = df[price_column].rolling(tick_threshold).apply(lambda x: x.iloc[0])
        df['Volume'] = df[volume_column].rolling(tick_threshold).sum()

        sampled_df = df[df['seq'] == tick_threshold - 1]
        sampled_df = sampled_df.drop(columns=['seq'])
        return sampled_df

    elif type(df) == SparkDataFrame:
        w = Window.orderBy(F.monotonically_increasing_id()).rowsBetween(1 - tick_threshold, 0)

        df = df.withColumn("seq",
                           (F.row_number().over(Window.orderBy(F.monotonically_increasing_id())) - 1) % tick_threshold)
        df = df.withColumn("Low", F.min(price_column).over(w))
        df = df.withColumn("High", F.max(price_column).over(w))
        df = df.withColumn("Close", F.last(price_column).over(w))
        df = df.withColumn("Open", F.first(price_column).over(w))
        df = df.withColumn("Volume", F.sum(volume_column).over(w))
        df = df.drop(*[price_column, volume_column])
        return df.filter(F.col("seq") == tick_threshold - 1).drop("seq")

