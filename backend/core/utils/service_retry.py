from typing import Callable, TypeVar
from backend.core.utils.dataclasses import BaseServiceResponse

T = TypeVar("T", bound=BaseServiceResponse)


def retry_handler(function: Callable[..., T], *args, retry_max_attempts: int = 3, **kwargs) -> T:
    attempts: int = 0

    while attempts < retry_max_attempts:
        response: T = function(*args, **kwargs)

        if response.failed:
            attempts += 1
            if attempts == retry_max_attempts:
                return response
            continue
        return response
    return response
