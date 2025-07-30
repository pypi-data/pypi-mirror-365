import logging
from contextlib import contextmanager
import _pytest  # noqa
import pytest
from pyspark.sql import SparkSession

logger = logging.getLogger('p3')


@pytest.fixture(scope='session')
def spark():
    """Yield SparkSession for testing session scope."""
    logger.info('Creating SparkSession...')
    spark = SparkSession.builder.master('local[*]').appName('spark_testing').getOrCreate()  # type: ignore

    logger.info('Set logLevel of py4j logger to ERROR')
    logging.getLogger('py4j').setLevel(logging.ERROR)
    yield spark

    # stop session after usage
    logger.info('Stopping SparkSession...')
    spark.stop()


@contextmanager
def can_execute():
    try:
        yield
    except Exception as e:
        raise pytest.fail(f"Wasn't able to execute function due to error: {e}")


@contextmanager
def not_raises(exception):
    try:
        yield
    except exception:
        raise pytest.fail(f'Did raise unwanted {exception}')


class SparkException(Exception): ...


class SparkItem(pytest.Item):
    def __init__(self, *, spec, **kwargs):
        super().__init__(**kwargs)
        self.spec = spec

    def runtest(self):
        for name, value in sorted(self.spec.items()):
            # Some custom test execution (dumb example follows).
            if name != value:
                raise SparkException(self, name, value)


# Introduce custom option for spark plugin
def pytest_addoption(parser):
    # spark remote url
    logger.info('The spark_remote_url and spark_conf options are without effect by now.')
    parser.addini('spark_remote_url', help='Remote URL for spark-connect')
    parser.addoption(
        '--spark-remote-url',
        dest='spark_remote_url',
        help='Remote URL for spark-connect',
    )
    parser.addini('spark_conf', help='Options to be used in SparkSession', type='linelist')


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'spark: signals that the respective test requires a SparkSession.',
    )


# # Hook specification for plugin
# def pytest_collection_modifyitems(session, config, items: Iterable[pytest.Item]):
#     """Mark tests that consume spark fixture with spark."""
#     for item in items:
#         logger.info(f'Collected Test: {item.name}')
#         if item.iter_markers('spark'):
#             logger.info('Encountered test marked with spark.')
#             if 'spark' not in item.fixturenames:  # type: ignore
#                 logger.warning('Test marked with spark does not consume spark fixture.')

#         if 'spark' in item.fixturenames and not item.iter_markers('spark'):  # type: ignore
#             logger.info('Added spark marker to test with spark fixture')
#             item.add_marker(pytest.mark.spark)
