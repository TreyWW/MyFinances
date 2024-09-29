# Invoices

Invoices allow you to bill customers for tasks or products. Customers can be sent an "invoice link" which allows them to view
the invoice via the dashboard, print out the invoice and pay the invoice.

## View an Invoice

You can find an invoice from the "`Invoices`" -> "`Single`" tab, where every invoice under your [Logged in Profile](#) will be
shown. Use the filters above each column to narrow down the list.

You can view an overview of the invoice by either clicking anywhere in the row, or the "three dots" -> "overview".

Here you can view things like the invoice status, ID, discounts, preview, and edit the invoice details.

## Invoice Statuses

Each invoice has a status: `draft`, `pending` or `paid`.

- **draft**: the invoice isn't yet finalised, you can easily make changes and get the invoice ready without the user
interacting or viewing details.
- **pending**: the invoice is ready for customer viewing and awaiting payment
- **overdue**: the invoice is still `pending`, however the due date has expired. You and the user can view the invoice as now
"overdue" - it's up to your business whether you add late fees.
- **paid**: the invoice has been fully (or partially) paid by the user and doesn't need modification


## Invoices vs Invoice Profiles

**Invoices** are invoice documents sent to customers to be paid. They have a status, products, total price, etc. **Invoice
Profiles** are sets of invoices that are often automatically created on a recurring basis, to be paid regularly. In an invoice
profile a normal **Invoice** is created every period. The profile just defines how often they are created, and the default
values attached to it.

# Invoice Profiles

As stated above, invoice profiles hold individual invoices and can be set to create a new invoice every period.

## Recurring Frequencies

- Weekly - choose a day of week, e.g. "mondays"
- Monthly - choose a day of month, e.g. "15th"
- Yearly - choose a day of month, e.g. "15th" and choose a month of year e.g. "january"

A single Invoice will be created every (period defined) and set to draft, you will be emailed automatically.

Invoices are created at `7am UTC` (`8am BST`) of each period, this is currently not customisable. Please contact us at
[enquiry@myfinances.cloud](mailto:enquiry@myfinances.cloud) if you require the flexibility.

The `end date` is when the automatic invoice creation will finish.
