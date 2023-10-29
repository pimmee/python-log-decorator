## Overview

Logging decorator that logs the arguments and return value of a function / method.

## Example usage

```py
from logcall import log

@log()
def foo(arg1, arg2, api_key):
    pass

class MyClass:
@log()
def my_method(self, arg1, arg2, api_key):
    pass

@log(ignore=["api_key"])
def foo(arg1, arg2, api_key):
    pass

```
