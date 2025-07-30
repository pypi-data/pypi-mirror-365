import logging
from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)


def test_spark_fixture(spark):
    """Assert fixture has correct type."""
    assert isinstance(spark, SparkSession)
