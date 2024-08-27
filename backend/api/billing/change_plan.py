from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import redirect, render

from backend.decorators import htmx_only
from backend.models import SubscriptionPlan, UserSubscription
from backend.types.requests import WebRequest
from backend.utils.calendar import timezone_now


# todo: this is only temporary


@htmx_only("billing:dashboard")
def change_plan_endpoint(request: WebRequest):

    plan: SubscriptionPlan = SubscriptionPlan.objects.filter(id=request.POST.get("plan_id")).first()
    print(type(plan))

    if plan and not plan.price_per_month == -1:
        print(type(plan))
        users_plans: QuerySet[UserSubscription] = UserSubscription.filter_by_owner(request.actor)
        users_active_plans: QuerySet[UserSubscription] = users_plans.filter(end_date__isnull=True)
        if users_active_plans.exists():
            for active_plan in users_active_plans:
                active_plan.end_date = timezone_now()
                active_plan.save()

        print(type(plan))

        UserSubscription.objects.create(owner=request.actor, subscription_plan=plan)
        messages.success(request, "Successfully changed subscription plan")
        r = HttpResponse(status=200)
        r["HX-Refresh"] = "true"
        return r
    else:
        messages.error(request, "Invalid plan or plan is enterprise")

    return render(request, "base/toast.html")
