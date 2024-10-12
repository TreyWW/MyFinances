from backend.clients.models import Client
from backend.core.service.clients.validate import validate_client_create
from backend.core.utils.dataclasses import BaseServiceResponse


class CreateClientServiceResponse(BaseServiceResponse[Client]): ...


def create_client(request, client_details_default: dict | None = None) -> CreateClientServiceResponse:
    client_details = client_details_default or {
        "name": request.POST.get("client_name"),
        "email": request.POST.get("client_email"),
        "address": request.POST.get("client_address"),
        "phone_number": request.POST.get("client_phone"),
        "contact_method": request.POST.get("client_contact_method"),
        "company": request.POST.get("company_name"),
        "is_representative": (True if request.POST.get("is_representative") == "on" else False),
    }

    error = validate_client_create(client_details)

    if error:
        return CreateClientServiceResponse(False, error_message=error)

    if request.user.logged_in_as_team:
        client = Client.objects.create(
            organization=request.user.logged_in_as_team,
        )
    else:
        client = Client.objects.create(
            user=request.user,
        )

    for model_field, new_value in client_details.items():
        setattr(client, model_field, new_value)

    client.save()
    return CreateClientServiceResponse(True, client)
