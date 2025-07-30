import logging
import pytest
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType
from pyspark.testing import assertDataFrameEqual, assertSchemaEqual
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)


class ExpectedDataFrame:
    """Context manager to use within a test.

    possible usage:
    with ExpectedDataFrame(df) as expected_df:
    or
    with ExpectedDataFrame.from_path(path_to_csv, "csv") as expected_df:
        expected_df == actual_df

    Usage as context manager should guarantee free memory after usage.
    """

    def __init__(self, df: DataFrame) -> None:
        self.df = df

    @classmethod
    def from_path(cls, path, format: str):
        spark = SparkSession.builder.getOrCreate()  # type: ignore
        df = spark.read.format(format).load(path)
        return cls(df)

    def __enter__(self):
        yield self

    def __exit__(self):
        """Remove References from cache."""
        self.df.unpersist()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DataFrame):
            return NotImplemented
        return all(
            [assertDataFrameEqual(self.df, other), assertSchemaEqual(self.df.schema, other.schema)]
        )


@runtime_checkable
class SparkTransformation(Protocol):
    """Protocol for Spark transformations receiving a DataFrame and returning one."""

    def __name__(self) -> str:  # type: ignore
        pass

    def __call__(self, df: DataFrame, *args, **kwargs) -> DataFrame:  # type: ignore
        pass


class Transformation:
    """Context manager to use within a test.

    possible usage:
    with Transformation(func) as test_logic:
        assert test_logic.runs_on_schema(schema)

    Usage as context manager should guarantee free memory after usage.
    """

    def __init__(self, func: SparkTransformation) -> None:
        self.func = func

    def __enter__(self):
        logger.info(f'Will test execution of transformation {self.func.__name__}.')
        yield self

    def runs_on_schema(self, schema: StructType):
        empty_df = Generator.create_empty_dataframe(schema)
        try:
            self.func(empty_df)
            return True
        except Exception as e:
            logger.error(f'Failed execution of function {self.func.__name__}: {e}')
            logger.debug(f'Tried execution on schema: {empty_df.printSchema()}')
            pytest.fail(str(e))

    def __exit__(self):
        logger.info(f'CleanUp test setup of transformation {self.func.__name__}.')


class Generator:
    @staticmethod
    def create_empty_dataframe(schema: StructType) -> DataFrame:
        spark = SparkSession.builder.getOrCreate()  # type: ignore
        logger.debug(f'Creating empty df with schema {schema}')
        empty_df = spark.createDataFrame([], schema)

        logger.debug('Empty df created successfully')
        return empty_df

    @staticmethod
    def create_dataframe(schema: StructType) -> DataFrame:
        raise NotImplementedError('Synthetic Data Generation is currently not supported')
