# Stripe API v2024-04-01 - Charges API & PaymentIntents

## Migration Notice: Charges to PaymentIntents

In Stripe API version `2024-04-01`, direct creation of `Charge` objects via `/v1/charges` is deprecated for customer-facing flows in favor of `PaymentIntents`.

## Create a Payment Intent

To initiate a payment flow:

```json
POST /v1/payment_intents
{
  "amount": 2000,
  "currency": "usd",
  "automatic_payment_methods": {
    "enabled": true
  }
}
```

### Response

The response includes a `client_secret` used by Stripe Elements on the frontend.
