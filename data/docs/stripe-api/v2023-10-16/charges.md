# Stripe API v2023-10-16 - Charges API

## Create a Charge

To charge a credit card or other payment source, create a `Charge` object.

```json
POST /v1/charges
{
  "amount": 2000,
  "currency": "usd",
  "source": "tok_visa",
  "description": "Charge for jenny.rosen@example.com"
}
```

### Parameters

- `amount` (integer, required): A positive integer representing how much to charge in the smallest currency unit (e.g., 100 cents to charge $1.00).
- `currency` (string, required): Three-letter ISO currency code, in lowercase. Must be a supported currency.
- `source` (string, optional): A payment source to be charged. This can be a token, a card ID, or a customer ID.
