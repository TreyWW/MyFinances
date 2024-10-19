from rest_framework.response import Response


def APIResponse(success: bool = True, data: str | dict | None = None, meta=None, status: int = 0, **kwargs) -> Response:
    """

    Returns a rest_framework Response object, but prefills meta (success etc) aswell as the data with KWARGS.

    """
    meta = meta or {}
    if not status and success:
        status = 201
    elif not status:
        status = 400

    if success:
        return Response({"meta": {"success": True, **meta}, "data": {**kwargs} | data if isinstance(data, dict) else {}}, status=status)
    else:
        return Response({"meta": {"success": False}, "error": data}, status=status)
