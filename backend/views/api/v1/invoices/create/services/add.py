from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(["POST"])
def add_service(request: HttpRequest):
    context = {}
    list_hours = request.POST.getlist("hours[]")
    list_service_name = request.POST.getlist("service_name[]")
    list_price_per_hour = request.POST.getlist("price_per_hour[]")
    list_of_current_rows = [
        row for row in zip(list_hours, list_service_name, list_price_per_hour)
    ]

    hours = int(request.POST.get("post_hours"))
    service_name = request.POST.get("post_service_name")
    price_per_hour = int(request.POST.get("post_price_per_hour"))

    if not hours:
        return JsonResponse(
            {"status": "false", "message": "The hours field is required"}, status=400
        )
    if not service_name:
        return JsonResponse(
            {"status": "false", "message": "The service name field is required"},
            status=400,
        )
    if not price_per_hour:
        return JsonResponse(
            {"status": "false", "message": "The price per hour field is required"},
            status=400,
        )

    context["rows"] = []
    for row in list_of_current_rows:
        context["rows"].append(
            {
                "hours": row[0],
                "service_name": row[1],
                "price_per_hour": row[2],
                "total_price": float(row[0]) * float(row[2]),
            }
        )

    context["rows"].append(
        {
            "hours": hours,
            "service_name": service_name,
            "price_per_hour": price_per_hour,
            "total_price": hours * price_per_hour,
        }
    )

    return render(
        request, "core/pages/invoices/create/_services_table_body.html", context
    )
