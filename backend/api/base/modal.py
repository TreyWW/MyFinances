from django.http import HttpRequest, HttpResponseBadRequest
from django.shortcuts import render

from backend.models import UserSettings, Invoice, Team


# Still working on


def open_modal(request: HttpRequest, modal_name, context_type=None, context_value=None):
    try:
        context = {}
        template_name = f"modals/{modal_name}.html"
        if context_type and context_value:
            if context_type == "profile_picture":
                try:
                    context["users_profile_picture"] = (
                        request.user.user_profile.profile_picture_url
                    )
                except UserSettings.DoesNotExist:
                    pass
            elif context_type == "accept_invite_with_code":
                context["code"] = context_value
            elif context_type == "leave_team":
                if request.user.teams_joined.filter(id=context_value).exists():
                    context["team"] = Team.objects.filter(id=context_value).first()
            elif context_type == "edit_invoice_to":
                invoice = context_value
                try:
                    invoice = Invoice.objects.get(user=request.user, id=invoice)
                except:
                    return render(request, template_name, context)

                if invoice.client_to:
                    context["to_name"] = invoice.client_to.name
                    context["to_company"] = invoice.client_to.company
                    context["to_address"] = invoice.client_to.address
                    context["existing_client_id"] = invoice.client_to.id
                    # context["to_city"] = invoice.client_to.city
                    # context["to_county"] = invoice.client_to.county
                    # context["to_country"] = invoice.client_to.country
                else:
                    context["to_name"] = invoice.client_name
                    context["to_company"] = invoice.client_company
                    context["to_address"] = invoice.client_address
                    # context["to_city"] = invoice.client_city
                    # context["to_county"] = invoice.client_county
                    # context["to_country"] = invoice.client_country
            else:
                context[context_type] = context_value

        return render(request, template_name, context)
    except Exception as e:
        print(f"Something went wrong with loading modal {modal_name}. Error: {e}")
        return HttpResponseBadRequest("Something went wrong")
