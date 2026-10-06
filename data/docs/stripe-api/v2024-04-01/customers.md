# Stripe API v2024-04-01 - Customers & Payment Methods

## Create a Customer with PaymentMethods

In Stripe API version `2024-04-01`, customer payment instruments are managed exclusively through `PaymentMethods` rather than legacy sources or card tokens.

```json
POST /v1/customers
{
  "email": "customer@example.com",
  "name": "Jane Doe",
  "metadata": {
    "tier": "enterprise"
  }
}
```

## SetupIntents for Saving Payment Methods

To securely collect and save customer payment credentials for future recurring billing without an immediate charge, use `SetupIntents`:

```json
POST /v1/setup_intents
{
  "customer": "cus_N9Klx0",
  "payment_method_types": ["card"]
}
```

The client application completes authentication via Stripe Elements with the returned `client_secret`.

## Customer Search API

Search for customers using structured query syntax:

```json
GET /v1/customers/search?query=email:'customer@example.com'
```
