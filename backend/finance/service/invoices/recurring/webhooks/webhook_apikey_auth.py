from core.api.public import APIAuthToken
from core.types.requests import WebRequest
from core.utils.dataclasses import BaseServiceResponse


class APIAuthenticationServiceResponse(BaseServiceResponse[None]):
    response: None = None
    _status_code: int


def authenticate_api_key(request: WebRequest) -> APIAuthenticationServiceResponse:
    auth_header = request.headers.get("Authorization")

    if not (auth_header and auth_header.startswith("Bearer ")):
        return APIAuthenticationServiceResponse(error_message="Unauthorized", status_code=401)

    token_key = auth_header.split(" ")[1]

    try:
        token = APIAuthToken.objects.get(
            hashed_key=APIAuthToken.hash_raw_key(token_key),
            active=True,
            administrator_service_type=APIAuthToken.AdministratorServiceTypes.AWS_WEBHOOK_CALLBACK,
        )

        if token.has_expired:
            return APIAuthenticationServiceResponse(error_message="Token expired", status_code=400)
    except APIAuthToken.DoesNotExist:
        return APIAuthenticationServiceResponse(error_message="Token not found", status_code=400)

    token.update_last_used()

    return APIAuthenticationServiceResponse(True, None, status_code=200)
