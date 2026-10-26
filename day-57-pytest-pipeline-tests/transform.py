ALLOWED_STATUSES = {"completed", "pending", "cancelled"}
TAX_RATE = 1.2


def normalize_order(raw):
    """Clean and validate a raw order record, returning a normalized
    version with a computed tax-inclusive total."""
    status = raw["status"].strip().lower()
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"invalid status: {status!r}")

    amount = float(raw["amount"])
    if amount < 0:
        raise ValueError(f"amount cannot be negative: {amount}")

    return {
        "order_id": raw["order_id"],
        "status": status,
        "amount": round(amount, 2),
        "amount_with_tax": round(amount * TAX_RATE, 2),
    }
