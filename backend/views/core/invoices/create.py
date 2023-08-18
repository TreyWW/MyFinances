from django.http import HttpRequest
from django.shortcuts import render


def create_invoice_page(request: HttpRequest):
    if request.method == "POST":
        for key, value in request.POST.items():
            print('Key: %s' % (key))
            # print(f'Key: {key}') in Python >= 3.7
            print('Value:  %s' % (value))

        print(f"list: {request.POST.getlist('good_name')}")
        print(f"list 2: {request.POST.getlist('good_quantity')}")
    return render(request, "core/pages/invoices/create/create.html")