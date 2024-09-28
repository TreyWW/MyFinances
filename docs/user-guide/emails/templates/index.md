# Email Templates

### Common Variables

| Variable         | Usage                                                                                   |
|------------------|-----------------------------------------------------------------------------------------|
| $first_name      | Displays the users first name                                                           |
| $invoice_id      | Displays the unique invoice ID                                                          |
| $invoice_ref     | Displays the invoice reference ID you may have attached                                 |
| $due_date        | Will display the date that the invoice is due (e.g. 12th December 2024)                 |
| $amount_due      | Will display the balance due for the invoice                                            |
| $currency        | Will display the currency TEXT used for the invoice (e.g. USD)                          |
| $currency_symbol | Will display the currency SYMBOL used for the invoice (e.g. $)                          |
| $product_list    | Will display a bullet point list of all product (names no descriptions)                 |
| $company_name    | Will display the company (or user) name of the sender                                   |
| $invoice_link    | Will provide a link that allows the user to view their invoice always up to date online |

### Examples

```
Hi $first_name,

The invoice $invoice_id has been created for you to pay, due on the $due_date. Please pay at your earliest convenience.

Balance Due: $amount_due $currency

Many thanks,
$company_name
```

may display

```
Hi John,

The invoice 0054 has been created for you to pay, due on the 13th of October. Please pay at your earliest convenience.

Balance Due: 150 USD

Many thanks,
Strelix
```
