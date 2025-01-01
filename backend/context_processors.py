from typing import Dict, Any

from core.types.requests import WebRequest
from backend import __version__


def extras(request: WebRequest):
    data: Dict[str, Any] = {}

    data["finances_version"] = __version__

    return data
