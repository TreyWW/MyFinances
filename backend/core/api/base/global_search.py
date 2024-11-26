from django.shortcuts import render

from backend.core.models import User, TeamMemberPermission
from backend.models import Client, Invoice


def global_search_endpoint(request):
    search_text = request.GET.get("search", "").strip().lower()

    # Mapping for pages
    page_mappings = {
        "dashboard": "/dashboard/",
        "receipts": "/dashboard/receipts/",
        "invoices single": "/dashboard/invoices/single/",
        "invoices recurring": "/dashboard/invoices/recurring/",
        "clients": "/dashboard/clients/",
        "file storage": "/dashboard/file_storage/",
        "settings": "/dashboard/settings/",
        "api keys": "/dashboard/settings/api_keys/",
    }

    # Available services
    services = {
        "dashboard": {
            "description": "Access your main dashboard",
            "icon": "fa-home",
            "url": page_mappings["dashboard"],
        },
        "invoices": {
            "description": "Simplify your billing for customers",
            "icon": "fa-file-invoice",
            "url": page_mappings["invoices single"],
            "features": {
                "Single": page_mappings["invoices single"],
                "Recurring": page_mappings["invoices recurring"],
            },
        },
        "clients": {
            "description": "Simplified customer information storage",
            "icon": "fa-users",
            "url": page_mappings["clients"],
            "features": {
                "View All": page_mappings["clients"],
                "Create new customer": f"{page_mappings['clients']}create/",
            },
        },
        "file storage": {
            "description": "Manage your files securely",
            "icon": "fa-folder",
            "url": page_mappings["file storage"],
        },
        "receipts": {
            "description": "Access your receipts",
            "icon": "fa-receipt",
            "url": page_mappings["receipts"],
        },
        "settings": {
            "description": "Configure system settings",
            "icon": "fa-cogs",
            "url": page_mappings["settings"],
            "features": {
                "API Keys": page_mappings["api keys"],
            },
        },
    }

    # Filter services based on search text
    filtered_services = {}
    for key, value in services.items():
        # Check if search_text matches service name
        if search_text in key.lower():
            filtered_services[key] = value
            continue

        # Check if search_text matches any feature name
        if "features" in value:
            for feature_name in value["features"]:
                if search_text in feature_name.lower():
                    filtered_services[key] = value
                    break

    resources = {
        "invoice": [],
        "client": [],
    }

    # Fetch only permitted clients
    def get_permitted_clients(request):
        if isinstance(request.actor, User):
            return Client.objects.filter(user=request.user)
        elif (
            request.team.is_owner(request.user)
            or "clients:read" in TeamMemberPermission.objects.filter(team=request.team, user=request.user).first().scopes
        ):
            return Client.objects.filter(organization=request.team)
        else:
            return Client.objects.none()

    # Fetch only permitted invoices
    def get_permitted_invoices(request):
        if isinstance(request.actor, User):
            return Invoice.objects.filter(user=request.user)
        elif (
            request.team.is_owner(request.user)
            or "clients:read" in TeamMemberPermission.objects.filter(team=request.team, user=request.user).first().scopes
        ):
            return Invoice.objects.filter(organization=request.team)
        else:
            return Invoice.objects.none()

    # Fetch resources only if search_text is present
    if search_text:
        # Track added IDs to avoid duplicates (duplicates appeared when I searched for exact client or Invoice)
        added_invoice_ids = set()
        added_client_ids = set()

        matched_filter = None  # To allow invoices to be searched by multiple queries
        # Fetch exact matches for Clients
        permitted_clients = get_permitted_clients(request)
        exact_client = permitted_clients.filter(name__iexact=search_text).first()
        if exact_client:
            resources["client"].append(
                {
                    "name": f"{exact_client.name} (#{exact_client.id})",
                    "url": f"{page_mappings['clients']}{exact_client.id}/",
                    "details": {
                        "Phone Number": f"{exact_client.phone_number}" if exact_client.phone_number else "N/A",
                        "Email": f"{exact_client.email}" if exact_client.email else "N/A",
                    },
                }
            )
            added_client_ids.add(exact_client.id)  # To avoid duplicates

        # Fetch partial matches for Clients
        partial_clients = permitted_clients.filter(name__icontains=search_text)
        for client in partial_clients:
            if client.id not in added_client_ids:  #  If current ID is not in already found ID's
                resources["client"].append(
                    {
                        "name": f"{client.name} (#{client.id})",
                        "url": f"{page_mappings['clients']}{client.id}/",
                        "details": {
                            "Phone Number": f"{client.phone_number}" if client.phone_number else "N/A",
                            "Email": f"{client.email}" if client.email else "N/A",
                        },
                    }
                )
                added_client_ids.add(client.id)  # To avoid duplicates

        # Save permitted invoices to variable
        permitted_invoices = get_permitted_invoices(request)

        if search_text.isdigit():
            # Fetch by ID if it's valid ID
            exact_invoice = permitted_invoices.filter(id=int(search_text)).first()
            if exact_invoice:
                resources["invoice"].append(
                    {
                        "name": f"{exact_invoice.client_company} (#{exact_invoice.id})",
                        "url": f"{page_mappings['invoices single']}{exact_invoice.id}",
                        "details": {
                            "Due Date": exact_invoice.date_due.strftime("%d/%m/%Y") if exact_invoice.date_due else "N/A",
                            "Total Amount": (
                                f"{exact_invoice.get_total_price()} {exact_invoice.currency}" if exact_invoice.get_total_price() else "N/A"
                            ),
                            "Client Name": exact_invoice.client_name,
                        },
                    }
                )

        else:
            # Fetch exact matches for Invoices
            exact_invoice = permitted_invoices.filter(client_name__iexact=search_text)
            if exact_invoice:
                matched_filter = "client_name"  # Save used filter
            else:
                # If no match for client_name, try client_company
                exact_invoice = permitted_invoices.filter(client_company__iexact=search_text)
                if exact_invoice:
                    matched_filter = "client_company"
            for invoice in exact_invoice:
                resources["invoice"].append(
                    {
                        "name": f"{invoice.client_name if matched_filter == 'client_name' else invoice.client_company} (#{invoice.id})",
                        "url": f"{page_mappings['invoices single']}{invoice.id}",
                        "details": {
                            "Due Date": invoice.date_due.strftime("%d/%m/%Y") if invoice.date_due else "N/A",
                            "Total Amount": f"{invoice.get_total_price()} {invoice.currency}" if invoice.get_total_price() else "N/A",
                            "Company" if matched_filter == "client_name" else "Client": (
                                invoice.client_company if matched_filter == "client_name" else invoice.client_name
                            ),
                        },
                    }
                )
                added_invoice_ids.add(invoice.id)  # To avoid duplicates

            # Fetch partial matches for Invoices
            partial_invoices = permitted_invoices.filter(client_name__icontains=search_text)
            if partial_invoices:
                matched_filter = "client_name"  # Save used filter
            else:
                # If no match for client_name, try client_company
                partial_invoices = permitted_invoices.filter(client_company__icontains=search_text)
                if partial_invoices:
                    matched_filter = "client_company"
            for invoice in partial_invoices:
                if invoice.id not in added_invoice_ids:  #  If current ID is not in already found ID's
                    resources["invoice"].append(
                        {
                            "name": f"{invoice.client_name if matched_filter == 'client_name' else invoice.client_company} (#{invoice.id})",
                            "url": f"{page_mappings['invoices single']}{invoice.id}",
                            "details": {
                                "Due Date": invoice.date_due.strftime("%d/%m/%Y") if invoice.date_due else "N/A",
                                "Total Amount": f"{invoice.get_total_price()} {invoice.currency}" if invoice.get_total_price() else "N/A",
                                "Company" if matched_filter == "client_name" else "Client": (
                                    invoice.client_company if matched_filter == "client_name" else invoice.client_name
                                ),
                            },
                        }
                    )
                    added_invoice_ids.add(invoice.id)  # To avoid duplicates

    return render(
        request,
        "base/topbar/_search_dropdown.html",
        {
            "services": filtered_services,
            "resources": resources,
            "resource_count": sum(len(v) for v in resources.values()),
            "search": search_text,
        },
    )
