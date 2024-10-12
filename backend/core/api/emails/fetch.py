from django.core.paginator import Paginator, Page
from django.db.models import Q, QuerySet
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django_ratelimit.core import is_ratelimited

from backend.decorators import web_require_scopes
from backend.models import EmailSendStatus
from backend.core.types.htmx import HtmxHttpRequest


@web_require_scopes("emails:read", True, True)
def fetch_all_emails(request: HtmxHttpRequest):
    if is_ratelimited(request, group="fetch_all_emails", key="user", rate="2/4s", increment=True) or is_ratelimited(
        request,
        group="fetch_all_emails",
        key="user",
        rate="5/10s",
        increment=True or is_ratelimited(request, group="fetch_all_emails", key="user", rate="20/2m", increment=True),
    ):
        return HttpResponse(status=429)
    context = {}
    if not request.htmx:
        return redirect("quotas")

    search_text = request.GET.get("search")
    page_num = request.GET.get("page")

    if request.user.logged_in_as_team:
        results: QuerySet[EmailSendStatus] = EmailSendStatus.objects.filter(organization=request.user.logged_in_as_team)
    else:
        results = EmailSendStatus.objects.filter(user=request.user)

    if search_text:
        results = results.filter(Q(recipient__icontains=search_text))

    result: Page | QuerySet = results.order_by("-id")

    paginator = Paginator(result, 8)
    result = paginator.get_page(page_num)

    context.update({"emails": result})
    return render(request, "pages/emails/_fetch_body.html", context)
