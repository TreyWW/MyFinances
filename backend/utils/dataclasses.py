from typing import TypeVar


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
