from django.utils import timezone

from backend.models import APIKey
from backend.types.requests import WebRequest
from backend.utils.dataclasses import BaseServiceResponse


class APIAuthenticationServiceResponse(BaseServiceResponse[None]):
    response: None = None
    _status_code: int


def authenticate_api_key(request: WebRequest) -> APIAuthenticationServiceResponse:
    token = request.headers.get("Authorization", "").split()
    print(token)

    if not token or token[0].lower() != "bearer":
        return APIAuthenticationServiceResponse(error_message="Unauthorized", status_code=401)

    if len(token) == 1:
        return APIAuthenticationServiceResponse(error_message="Token not found", status_code=400)

    if len(token) > 2:
        return APIAuthenticationServiceResponse(error_message="Invalid token. Token should not contain spaces.", status_code=400)

    try:
        key_id = token[1].split(":")[0]
        key_str = token[1].split(":")[1]
        print(key_id)
        apikey = APIKey.objects.get(id=key_id)
        print(apikey)

        correct = apikey.verify(token[1])
        print(correct)
    except APIKey.DoesNotExist:
        return APIAuthenticationServiceResponse(error_message="Token not found", status_code=400)
    except ValueError:
        return APIAuthenticationServiceResponse(error_message="Invalid token", status_code=400)

    if not correct:
        return APIAuthenticationServiceResponse(error_message="Token not found", status_code=400)

    apikey.last_used = timezone.now()
    apikey.save()

    return APIAuthenticationServiceResponse(True, None, status_code=200)
