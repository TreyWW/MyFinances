from backend.models import Client
from backend.service.clients.validate import validate_client_create
from backend.service.defaults.get import get_account_defaults


def create_client(request, client_details_default: dict | None = None) -> str | Client:
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
        return error

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
    return client
