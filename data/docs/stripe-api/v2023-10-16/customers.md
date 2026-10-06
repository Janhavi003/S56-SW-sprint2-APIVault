# Stripe API v2023-10-16 - Customers API

## Create a Customer

In Stripe API version `2023-10-16`, you create customer objects to manage recurring billing, store card tokens, and track invoice history.

```json
POST /v1/customers
{
  "email": "customer@example.com",
  "name": "Jane Doe",
  "description": "Premium subscriber",
  "source": "tok_123456789"
}
```

### Parameters

- `email` (string, optional): The customer's primary email address.
- `name` (string, optional): The customer's full name.
- `source` (string, optional): A payment source token (e.g., `tok_visa`) to attach as the default payment source.

## Retrieve and Update Customer

Retrieve customer details using the customer ID:

```json
GET /v1/customers/cus_N9Klx0
```
