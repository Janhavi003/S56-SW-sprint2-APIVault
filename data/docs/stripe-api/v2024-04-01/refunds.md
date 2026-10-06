# Stripe API v2024-04-01 - Refunds & Disputes API

## Create a Refund via PaymentIntent

In Stripe API version `2024-04-01`, refunds can be created directly using a `PaymentIntent` ID or a `Charge` ID.

```json
POST /v1/refunds
{
  "payment_intent": "pi_3MtwEN2eZvKYlo2C0VvW3S89",
  "amount": 1500,
  "reason": "requested_by_customer"
}
```

### Parameters

- `payment_intent` (string, optional): ID of the PaymentIntent to refund.
- `charge` (string, optional): ID of the Charge to refund.
- `amount` (integer, optional): Amount in cents to refund.

## Dispute Evidence Submission

Manage chargeback disputes programmatically:

```json
POST /v1/disputes/dp_1MtwEZ2eZvKYlo2C9kP1bX9Z
{
  "evidence": {
    "customer_communication": "file_1MtwEZ2eZvKYlo2C0VvW3S89",
    "uncategorized_text": "Customer confirmed order receipt via email."
  }
}
```
