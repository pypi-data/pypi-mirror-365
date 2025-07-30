# Pytest PySpark Plugin or simply p3

Pytest pyspark plugin for testing. Contains help functions for data asserting, encryption, creation and more upcoming.

## Why tho'?
With the efficient testing capabilities in pyspark's [testing module](https://spark.apache.org/docs/latest/api/python/getting_started/testing_pyspark.html), why would one need a pyspark plugin for pytest?

First up, I'm a big fan of pytest in comparison to unittest due to its more pythonic feel to me w.r.t ease of use and code simplicity. Although the deeper you go down the rabbit hole of writing tests in pytest the more complicated it gets :alembic:. Therefore, the sole reason why I started writing this was the following:

I want to have the pytest feel when testing pyspark code. I want to be able to test my code against different environments (from synthetic or artificial test data up to production data) in an automated manner without duplicate code handling. And I want to learn stuff of course.


### The dilemma of testing data transformation logic
Testing in an environment of data-engineering is a complicated topic. Asserting your implemented business logic is correct by asserting Input and Output of a function is the bare minimum, but far from guaranteeing a correct implementation.

Let me explain this by a simple example:

Imagine the following dataframe 
|Country|State|City|
|---|---|---|
|Germany|Bavaria|Munich|
|Germany|Bavaria|Nuremberg|
|Spain|Catalonia|Barcelone|

Then assume you want to have the registered number of cities in a country. It's grouping by country and counting distinct values of city column. So the output shall be
|Country|Cities|
|---|---|
|Germany|2|
|Spain|1|


If our test is simply asserting the output dataframe is equal to the previous table is a first step into asserting correct functionality but not sufficient!


Assume the following functions:
```python
from pyspark.sql import functions as F, DataFrame, SparkSession

def count_distinct_cities(df: DataFrame) -> DataFrame:
    return df.groupBy("Country").agg(F.countDistinct("City").alias("Cities"))

def count_cities(df: DataFrame) -> DataFrame:
    return df.groupBy("Country").agg(F.count("City").alias("Cities"))

def hardcode_city_counts(df: DataFrame) -> DataFrame:
    data = [{"Country": "Germany", "Cities": 2}, {"Country": "Spain", "Cities": 1}]
    return SparkSession.builder.getOrCreate().createDataFrame(data)
```

All of the above functions will pass the test although only the first one has the correct logic implemented.

This pytest plugin aims to create a useful baseline for spark unit testing. Therefore several help functions and classes are introduced in order to make writing tests easy and joyful.

## :tada: Feature Description :sparkles:

### SparkSession Fixture
A Spark Session, optimized for standalone or 0-Worker Cluster is provided with minimal shuffling and other configurations.

### Markers
The plugin adds a new marker to pytest, `@pytest.mark.spark` which marks the test to require a running spark session.

One can then run all tests that require spark with the following command:
```sh
pytest -m spark
```

or respectively, if all but spark marked tests should run
```sh
pytest -m not spark
```


## :alembic: Vision :construction:

The following features are currently under preparation (so will definitely be part of the plugin in the near future but not yet finished)

### :globe_with_meridians: Exchangeable SPARK_REMOTE URL/ Spark-Connect support
I want to be able to exchange the spark server in the cli. MAybe first I want to run a job offline against a locally running spark connect server and in the next test I want to use a Databricks Cluster because I'm running Integration tests or need to have production-like data.

```sh
pytest -m spark --spark-remote "sc://localhost:15001"
```

### :wrench: SparkSession Config in config file `pytest.ini` or `pyproject.toml` or Command-Line
Similar to previous feature I want configure some stuff early on either in the command line or in a config file.

```sh
pytest -m spark --spark-conf "spark.sql.shuffle.partitions=100"
```


### Runs On Schema or Can Build Execution Plan
As a more base test, one may test if the function (Transformation) can be applied on a DataFrame with a specific schema. Therefore the least test one should write would be the test whether or not the function runs on a dataframe with a specific schema

```python
def test_transformation(spark, schema: StructType) -> None

```

### Under further evaluation

I'm still figuring out if these are necessary and a good practice but somehow they're appealing.

1. **Test-based/parametrized SparkSession Config override**

I would love to test different transformations on different configurations. Maybe for a transformation some configuration is necessary, so I would love to (re-)configure the `SparkSession` before the test run and set it back afterwards. 

```python
@pytest.mark.spark
@configure_spark(**options)
def test_transformation(spark, input_df) -> None:
    do_something()
```

2. **Auto-Ingest spark session fixture into marked tests**


## Contributing
> **__NOTE__**: Since this is mainly WIP for now, prepare yourself to face some issues. I'll try to keep everything updated.

### Developer Setup
The following tools are currently used:
**Python**
I am using python 3.12.9 but project should support everything up from 3.11.

**Java**
I am using java version 21 via openjdk. But with Spark-Connect used, this can be abandoned.

**Project Management: uv**
I recommend latest version which currently is 0.7.x
```sh
curl -LsSf https://astral.sh/uv/0.7.x/install.sh | sh
```

**Dev Tools**
Dev Tools correlate to pre-commit hooks and besides pre-commit are optional. I recommend installing `ruff` and `pyrefly` next to pre-commit

```sh
uv tool install pre-commit
```

## Contact
If you have any questions either use the GitHub Issues section or reach out to our maintainer(s)

</br>

>**Mike Fischer**
>
>Data Solutions Engineer
