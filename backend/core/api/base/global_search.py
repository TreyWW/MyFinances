from django.shortcuts import render
from django.urls import reverse

from backend.core.types.requests import WebRequest


def global_search_endpoint(request: WebRequest):
    services = {
        "invoices": {
            "description": "Simplify your billing for customers",
            "icon": "fa-file-invoice",
            "url": reverse("finance:invoices:single:dashboard"),
            "features": {
                "Single": reverse("finance:invoices:single:dashboard"),
                "Recurring": reverse("finance:invoices:recurring:dashboard")
            }
        },
        "clients": {
            "description": "Simplified customer information storage",
            "icon": "fa-users",
            "url": reverse("clients:dashboard"),
            "features": {
                "View All": reverse("clients:dashboard"),
                "Create new customer": reverse("clients:create")
            }
        }
    }

    resources = {
        "invoice": [
            {
                "name": "#23",
                "details": {
                    "Due Date": "12/11/2024",
                    "Total Amount": "£1,333"
                }
            },
            {
                "name": "#24",
                "details": {
                    "Due Date": "23/11/2024",
                    "Total Amount": "£433.20"
                }
            }
        ],
        "client": [
            {
                "name": "Bob Smith (#21)",
                "details": {
                }
            },
            {
                "name": "Jeff Smith (#22)",
                "details": {
                }
            }
        ]
    }

    return render(
        request, "base/topbar/_search_dropdown.html", {
            "services": services,
            "resources": resources,
            "resource_count": sum(len(v) for v in resources.values()),
            "search": request.GET.get("search")
        }
    )
