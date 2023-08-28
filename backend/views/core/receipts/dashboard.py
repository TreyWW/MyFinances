from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from backend.models import Receipt, UserSettings


@login_required
def receipts_dashboard(request: HttpRequest):
    if request.htmx:
        search_text = request.POST.get('search')
        results = Receipt.objects.filter(user=request.user).filter(Q(name__icontains=search_text) | Q(date__icontains=search_text))
        return render(request, 'core/pages/receipts/_search_results.html', {'receipts': results})

    reversed_new = reverse_lazy('api v1 receipts new')

    context = {"modal_data": [{
        "id": "receipt-modal",
        "title": "Upload a receipt",
        "action": {
            "text": "Add Receipt", "method": "post",
            "extra": f"enctype=multipart/form-data hx-post={reversed_new} hx-target=#items",
            "fields": [
                {
                    "type": "text", "name": "receipt_name",
                    "required": False, "label": "Receipt name", "placeholder": "Black Pen"
                },
                {
                    "type": "file", "name": "receipt_image",
                    "required": True, "extra": 'accept=image/png,image/jpeg',
                },
                {
                    "type": "date", "name": "receipt_date",
                    "required": True, "label": "Receipt date",
                }

            ]
        }
    }],
        'receipts': Receipt.objects.filter(user=request.user).order_by('date')
    }

    return render(request, "core/pages/receipts/dashboard.html", context)
