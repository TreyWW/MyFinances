import datetime
import functools
import logging

from rest_framework.response import Response

logger = logging.getLogger(__name__)


# add type hints for these deprecation dates


def deprecated(deprecation_date: datetime.datetime | None = None, end_of_life_date: datetime.datetime | None = None):
    """
    Returns a decorator which informs requester that the decorated endpoint has been deprecated.
    """

    def decorator_deprecated(func):
        """Amend the request with information that the endpoint has been deprecated and when it will be removed"""

        @functools.wraps(func)
        def wrapper_deprecated(*args, **kwargs):
            # do something before handling the request, could e.g. issue a django signal
            logger.warning("Deprecated endpoint %s called", func.__name__)

            if end_of_life_date and datetime.datetime.now() > end_of_life_date:
                return Response(
                    {"success": False, "message": "This endpoint is no longer available"},
                    status=410,
                    headers={"X-Deprecated": "", "X-Deprecation-Date": deprecation_date, "X-End-Of-Life-Date": end_of_life_date},
                )

            response: Response = func(*args, **kwargs)

            # amend the response with deprecation information
            if isinstance(response, Response):
                response.headers["X-Deprecated"] = ""
                if deprecation_date:
                    response.headers["X-Deprecation-Date"] = deprecation_date
                if end_of_life_date:
                    response.headers["X-End-Of-Life-Date"] = deprecation_date
            return response

        return wrapper_deprecated

    return decorator_deprecated
