import pytest
from pyspark.sql.types import (
    BooleanType,
    DoubleType,
    IntegerType,
    LongType,
    StringType,
    StructField,
    StructType,
)
from p3._internals import Generator


@pytest.fixture
def schema():
    return StructType(
        [
            StructField('string', StringType(), True),
            StructField('double', DoubleType(), True),
            StructField('integer', IntegerType(), True),
            StructField('long', LongType(), True),
            StructField('bool', BooleanType(), True),
        ]
    )


def test_empty_df_generation(schema) -> None:
    df = Generator.create_empty_dataframe(schema)
    assert {'string', 'double', 'integer', 'long', 'bool'} == set(df.columns)
    assert df.count() == 0


def test_not_implemented_data_generation(schema) -> None:
    with pytest.raises(NotImplementedError):
        Generator.create_dataframe(schema)
