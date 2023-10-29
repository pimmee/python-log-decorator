import logging
import pytest

from log_decorator import log


@log(ignore=["api_key"])
def foo(x, y, api_key):
    return x + y


class MyClass:
    @log(ignore=["api_key"])
    def foo(self, x, y, api_key):
        return x + y


@pytest.fixture
def caplog(caplog):
    caplog.set_level(logging.DEBUG)
    return caplog


def test_function_log(caplog):
    # given, when
    result = foo(1, y=2, api_key="my_secret_key")

    # then
    assert result == 3
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "DEBUG"
    log_message = caplog.records[0].message
    assert (
        log_message
        == "foo successfully called {'args': {'x': 1, 'y': 2, 'api_key': '**SECRET**'}, 'return_value': 3}"
    )


def test_function_error_log(caplog):
    with pytest.raises(TypeError):
        foo("a", 2, api_key="my_secret_key")

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"

    log_message = caplog.records[0].message
    assert (
        log_message
        == "foo encountered an error {'args': {'x': 'a', 'y': 2, 'api_key': '**SECRET**'}, 'error': 'can only concatenate str (not \"int\") to str'}"
    )


def test_class_method_log(caplog):
    # given, when
    result = MyClass().foo(1, y=2, api_key="my_secret_key")
    # then
    assert result == 3
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "DEBUG"
    log_message = caplog.records[0].message
    assert (
        log_message
        == "MyClass::foo successfully called {'args': {'x': 1, 'y': 2, 'api_key': '**SECRET**'}, 'return_value': 3}"
    )


def test_class_method_error_log(caplog):
    # given
    with pytest.raises(TypeError):
        MyClass().foo("a", 2, api_key="my_secret_key")

    # then
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"
    log_message = caplog.records[0].message
    assert (
        log_message
        == "MyClass::foo encountered an error {'args': {'x': 'a', 'y': 2, 'api_key': '**SECRET**'}, 'error': 'can only concatenate str (not \"int\") to str'}"
    )
