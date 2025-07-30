def pytest_generate_tests(metafunc):
    test_ids = []
    argvalues = []
    for exception, message in metafunc.cls.exception_tests:
        test_ids.append(exception.__name__)
        argvalues.append([exception(message), message])
    metafunc.parametrize(['exception_class', 'message'], argvalues, ids=test_ids, scope='class')


class TestException:
    exception_tests = [
        # append new exceptions and messages here
        # (ExceptionClass, "message")
    ]

    def test_correct_exception_message(self, exception_class, message) -> None:
        assert exception_class.message == message

    def test_correct_stringification(self, exception_class, message) -> None:
        assert str(exception_class) == message
