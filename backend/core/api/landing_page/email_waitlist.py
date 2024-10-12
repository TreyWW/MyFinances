from textwrap import dedent

from login_required import login_not_required

from backend.core.service import BOTO3_HANDLER
from backend.core.types.requests import WebRequest

from django.http import HttpResponse

from settings.helpers import send_email


@login_not_required
def join_waitlist_endpoint(request: WebRequest):
    email_address = request.POST.get("email", "")
    name = request.POST.get("name", "")

    if not email_address:
        return HttpResponse(status=400)

    if not BOTO3_HANDLER.initiated:
        return HttpResponse(status=500)

    BOTO3_HANDLER.dynamodb_client.put_item(TableName="myfinances-emails", Item={"email": {"S": email_address}, "name": {"S": name}})

    content = """
        <div class='text-success'>
            Successfully registered! Expect some discounts and updates as we progress in our journey :)
        </div>
    """

    send_email(
        destination=email_address,
        subject="Welcome aboard",
        content=dedent(
            f"""
                Thank you for joining our waitlist!

                We're excited to have you on board and will be in touch with more updates as we progress in our journey.

                Stay tuned for discounts, updates and personal direct emails from our founder!

                Best regards,
                The MyFinances Team
            """
        ).strip(),
    )

    return HttpResponse(status=200, content=dedent(content).strip())
