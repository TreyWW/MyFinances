from textwrap import dedent


def recurring_invoices_invoice_created_default_email_template() -> str:
    return dedent(
        """
    Hi $first_name,

    The invoice #$invoice_id has been created for you to pay, due on the $due_date. Please pay at your earliest convenience.

    Balance Due: $currency_symbol$amount_due $currency

    Many thanks,
    $company_name
    """
    ).strip()


def recurring_invoices_invoice_overdue_default_email_template() -> str:
    return dedent(
        """
    Hi $first_name,

    The invoice #$invoice_id is now overdue. Please pay as soon as possible to avoid any interruptions in your service or late fees.

    Balance Due: $currency_symbol$amount_due $currency

    Many thanks,
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
        "\n"
        + dedent(
            """
Note: This is an automated email sent out by MyFinances on behalf of '$company_name'.

If you believe this is spam or fraudulent please report it to us at report@myfinances.cloud and DO NOT pay the invoice.
Once a report has been made you will have a case opened. Eligible reports may receive a reward, decided on a case by case basis.
"""
        ).strip()
    )
