from typing import Any, Callable, List, TypeVar, cast
import functools
import logging
import inspect

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Callable[..., Any])


def is_class_method(args: tuple) -> bool:
    """
    Check if the function is a class method by examining the first argument.
    """
    return (
        bool(args)
        and hasattr(args[0], "__class__")
        and not isinstance(args[0], (int, float, str, list, dict, tuple))
    )


def convert_args_to_kwargs(func: T, args: tuple, kwargs: dict) -> dict:
    """
    Convert all arguments to keyword arguments for better logging.
    """
    param_names = list(inspect.signature(func).parameters.keys())
    if is_class_method(args):
        param_names = param_names[1:]
        args = args[1:]
    all_kwargs = {k: v for k, v in zip(param_names, args)}
    all_kwargs.update(kwargs)
    return all_kwargs


SECRET_KEYS = ["api_key", "access_token", "email"]


def sanitize_kwargs(kwargs: dict, ignore_keys: List[str]) -> dict:
    """
    Redact secret keys in the logging data.
    """
    secret_keys = SECRET_KEYS + ignore_keys
    return {k: ("**SECRET**" if k in secret_keys else v) for k, v in kwargs.items()}


def log(ignore: List[str] = []) -> Callable[[T], T]:
    """
    Decorator for logging function or method calls and their outcomes.
    @param ignore: List of argument keys to ignore in the logging data.
    """

    def decorator(func: T) -> T:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            all_kwargs = convert_args_to_kwargs(func, args, kwargs)
            sanitized_kwargs = sanitize_kwargs(all_kwargs, ignore_keys=ignore)
            class_name = args[0].__class__.__name__ if is_class_method(args) else None
            prefix = f"{class_name}:{func.__name__}" if class_name else func.__name__

            try:
                result = func(*args, **kwargs)  # Call the original function/method
                message = f"{prefix} successfully called"
                data = {"args": sanitized_kwargs, "return_value": result}
                logger.debug(f"{message} {data}")
                return result
            except Exception as e:
                message = f"{prefix} encountered an error"
                data = {
                    "args": sanitized_kwargs,
                    "error": str(e),
                    # "stack": traceback.format_exc(),
                }
                logger.error(f"{message} {data}")
                raise e  # Re-raise the original exception

        return cast(T, wrapper)

    return decorator
