# Stripe API v2023-10-16 - Refunds API

## Create a Refund

Create a refund for a previously settled charge using the `Charge` ID.

```json
POST /v1/refunds
{
  "charge": "ch_3MtwEN2eZvKYlo2C0VvW3S89",
  "amount": 1000,
  "reason": "requested_by_customer"
}
```

### Parameters

- `charge` (string, required): The identifier of the charge to refund.
- `amount` (integer, optional): A positive integer in cents representing the partial refund amount. If omitted, the entire charge will be refunded.
- `reason` (string, optional): String indicating the reason for the refund (`duplicate`, `fraudulent`, or `requested_by_customer`).
