from dataclasses import dataclass
from typing import TypeVar, Any, Optional, Generic

T = TypeVar("T")


def extract_to_dataclass(request, class_type: T, request_types: list[str], *args, **kwargs) -> T:
    """

    Turn kwargs from Key:Value and get request.POST.get(value) and set class.key = request.POST.get(value)

    Usage:

    from pydantic.dataclasses import dataclass
    from typing import Optional

    @dataclass
    class MyView:
        name: str
        age: int
        different: bool
        non_required: Optional[str]

    def myview(request):
        try:
            data = extract_to_dataclass(request, MyView, ["post"], "name", "age", diff_bool="different")
        except pydantic.ValidationError:
            pass
    """
    data: dict = {}
    if "get" in request_types:
        if args:
            data |= {key: request.GET.get(key) for key in args}

        if kwargs:
            data |= {key: request.GET.get(value) for key, value in kwargs.items()}

    if "post" in request_types:
        if args:
            data |= {key: request.POST.get(key) for key in args}

        if kwargs:
            data |= {key: request.POST.get(value) for key, value in kwargs.items()}

    if "headers" in request_types:
        if args:
            data |= {key: request.headers.get(key) for key in args}

        if kwargs:
            data |= {key: request.headers.get(value) for key, value in kwargs.items()}

    if isinstance(class_type, type):
        return class_type(**data)
    else:
        raise TypeError("class_type must be a class")


class BaseServiceResponse(Generic[T]):
    _success: bool = False
    _response: Optional[T] = None
    _error_message: str = ""
    _status_code: Optional[int] = None

    def __init__(self, success: bool = False, response: Optional[T] = None, error_message: str = "", status_code: Optional[int] = None):
        self._success = success
        self._response = response
        self._error_message = error_message
        self._status_code = status_code

    @property
    def success(self) -> bool:
        if not isinstance(self._success, bool):
            raise TypeError("success must be a boolean")

        return self._success

    @property
    def response(self) -> T:
        if self._response is None:
            raise TypeError("response must be present if it was a successful response")
        return self._response

    @property
    def error_message(self) -> str:
        if not isinstance(self._error_message, str):
            raise TypeError("error_message must be a string")
        return self._error_message

    @property
    def status_code(self) -> int:
        if not isinstance(self._status_code, int):
            raise TypeError("status code must be an integer")
        return self._status_code

    @property
    def failed(self) -> bool:
        return not self.success

    @property
    def error(self) -> str:
        return self.error_message if self.failed else "Unknown error"

    def __post_init__(self):
        if self.success and self.response is None:
            raise ValueError("Response cannot be None when success is True.")
        if not self.success and self.response is not None:
            raise ValueError("Response must be None when success is False.")
        if not self.success and not self.error_message:
            raise ValueError("Error message cannot be empty when success is False.")


# * BaseServiceResponse Usage

# from backend.utils.dataclasses import BaseServiceResponse
#
#
# class XyzServiceResponse(BaseServiceResponse[ResponseObject]):
#     response: Optional[ResponseObject] = None
# or
# ...

# * Return Response

# return CreateClientServiceResponse(False, error_message="my error")
# return CreateClientServiceResponse(False, ClientObject)

# * View Usage
#
# client_response: CreateClientServiceResponse = create_client(request)
#
# if client_response.failed:
#     print(client_response.error)
# else:
#     print(client_response.response) # < ClientObject>
