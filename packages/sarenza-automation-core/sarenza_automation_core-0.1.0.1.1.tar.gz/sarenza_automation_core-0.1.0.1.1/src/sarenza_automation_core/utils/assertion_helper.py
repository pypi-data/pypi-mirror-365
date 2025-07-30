from functools import wraps


def assert_with_message(message: str):
    """
    A decorator that automatically asserts the return value of a function
    and raises an AssertionError with a custom message if the assertion fails.

    :param message: Custom message to include if the assertion fails.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if not result:
                raise AssertionError(message)
            return result

        return wrapper

    return decorator
