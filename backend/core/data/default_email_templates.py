from textwrap import dedent


def recurring_invoices_invoice_created_default_email_template() -> str:
    return dedent(
        """
        Hi $first_name,

        Your invoice #$invoice_id is now available and is due by $due_date. Please make your payment at your earliest convenience.

        Balance Due: $currency_symbol$amount_due $currency
        View or Pay Online: $invoice_link
        If you are paying by standing order, no further action is required. Should you have any questions or concerns, feel free to reach out to us.

        Thank you for your prompt attention to this matter.

        Best regards,
        $company_name
    """
    ).strip()


def recurring_invoices_invoice_overdue_default_email_template() -> str:
    return dedent(
        """
    Hi $first_name,

    We wanted to remind you that invoice #$invoice_id is now overdue. Please arrange payment as soon as possible to ensure there’s no interruption in your service. If you’ve already made the payment, kindly disregard this message—our apologies for any confusion.

    Here are the details for your convenience:

    Balance Due: $currency_symbol$amount_due $currency
    Due Date: $due_date

    If you have any questions or concerns, we’re happy to help. Please don’t hesitate to reach out.

    Thank you for your prompt attention to this matter.

    Warm regards,
    $company_name
    """
    ).strip()


def recurring_invoices_invoice_cancelled_default_email_template() -> str:
    return dedent(
        """
    Hi $first_name,

    The invoice #$invoice_id has been cancelled. You do not have to pay the invoice.

    If you have any questions or concerns, please feel free to contact us.

    Many thanks,
    $company_name
    """
    ).strip()


def email_footer() -> str:
    return (
        "\n\n"
        + dedent(
            """
        Note: This is an automated email sent by MyFinances on behalf of '$company_name'.

        If you believe this email is spam or fraudulent, please do not pay the invoice and report it to us immediately at report@myfinances.cloud.
        Once reported, we will open a case for investigation. In some cases, eligible reports may qualify for a reward, determined on a case-by-case basis.
        """
        ).strip()
    )
