from pyspark.sql import DataFrame
from p3._internals import SparkTransformation


def limit_df(df: DataFrame, n: int = 5) -> DataFrame:
    """Limit the DataFrame to the first n rows."""
    return df.limit(n)


def test_protocol_success() -> None:
    # TODO this is a bad test, I believe any callable will pass
    # FIXME
    assert isinstance(limit_df, SparkTransformation)
