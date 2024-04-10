from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django_ratelimit.core import is_ratelimited
from django_ratelimit.decorators import ratelimit

from backend.models import EmailSendStatus


def fetch_all_emails(request: HttpRequest):
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
        results = EmailSendStatus.objects.filter(organization=request.user.logged_in_as_team)
    else:
        results = EmailSendStatus.objects.filter(user=request.user)

    if search_text:
        results = results.filter(Q(recipient__icontains=search_text))

    results = results.order_by("-id")

    paginator = Paginator(results, 8)
    results = paginator.get_page(page_num)

    context.update({"emails": results})
    return render(request, "pages/emails/_fetch_body.html", context)
