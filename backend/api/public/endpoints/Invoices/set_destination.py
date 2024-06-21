from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from backend.models import Client
from backend.api.public.serializers.clients import ClientSerializer


to_get = ["name", "address", "city", "country", "company", "is_representative"]


@api_view(["POST"])
def set_destination_from_endpoint(request):
    context: dict = {"swapping": True}

    data = request.data
    context.update({key: data.get(key, "") for key in to_get})

    return Response(context, status=status.HTTP_200_OK)


@api_view(["POST"])
def set_destination_to_endpoint(request):
    context: dict = {"swapping": True}

    data = request.data
    context.update({key: data.get(key, "") for key in to_get})

    use_existing = True if request.data.get("use_existing") == "true" else False
    selected_client = request.data.get("selected_client") if use_existing else None

    if selected_client:
        try:
            client = Client.objects.get(user=request.user, id=selected_client)
            context["existing_client"] = ClientSerializer(client).data
        except Client.DoesNotExist:
            return Response({"detail": "Client not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(context, status=status.HTTP_200_OK)
