from pytest import Pytester

COLLECTION_FILE = """
import pytest

@pytest.mark.spark
def test_spark_marker():
    assert True

def test_marker_deselection():
    assert True
"""

CONFTEST_FILE = """
import pytest
pytest_plugins = ["p3"]
"""


def test_active_plugin(pytester: Pytester):
    # create a temporary conftest.py file
    pytester.makeconftest(CONFTEST_FILE)

    # create a temporary pytest test file
    pytester.makepyfile(COLLECTION_FILE)
    res = pytester.runpytest()
    plugins_line = [s for s in res.outlines if s.startswith('plugins:')][0]
    assert 'pyspark-plugin' in plugins_line


def test_available_fixtures(pytester: Pytester):
    # create a temporary conftest.py file
    pytester.makeconftest(CONFTEST_FILE)
    res = pytester.runpytest('--fixtures')
    assert any('spark [session scope]' in line for line in res.stdout.lines)


def test_oppressing_plugin(pytester: Pytester):
    # create a temporary conftest.py file
    pytester.makeconftest(CONFTEST_FILE)
    res = pytester.runpytest('-p no:p3')
    assert not any('spark [session scope]' in line for line in res.outlines)


def test_spark_marker(pytester: Pytester):
    """Make sure that plugin works."""
    # create a temporary conftest.py file
    pytester.makeconftest(CONFTEST_FILE)

    # create a temporary pytest test file
    pytester.makepyfile(COLLECTION_FILE)

    # run all tests with spark marker
    result = pytester.runpytest('--collect-only', '-m spark')

    # check that all 4 tests passed
    # We deselect the test that uses spark fixture tho, tbd.
    result.assert_outcomes(deselected=1)


# @pytest.mark.xfail(reason='still select tests using SparkSession fixture.')
def test_no_spark_marker(pytester: Pytester):
    """Make sure that plugin works."""
    pytester.makeconftest(CONFTEST_FILE)
    pytester.makepyfile(COLLECTION_FILE)

    # run all tests without spark marker
    # Doesnt work at the moment due to string representation
    result = pytester.runpytest('-m not spark', '--collect-only')

    # check that all 4 tests passed
    # Still problem with
    result.assert_outcomes(deselected=1)
