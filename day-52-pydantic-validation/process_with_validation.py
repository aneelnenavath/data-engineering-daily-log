from pydantic import ValidationError

from order_model import Order
from raw_orders import RAW_ORDERS

print("Processing orders with Pydantic validation...\n")

total_revenue = 0.0
processed = 0
failed = 0

for raw in RAW_ORDERS:
    try:
        order = Order(**raw)
    except ValidationError as e:
        failed += 1
        order_id = raw.get("order_id", "UNKNOWN")
        print(f"Order {order_id}: REJECTED")
        for err in e.errors():
            field = ".".join(str(p) for p in err["loc"])
            print(f"    field={field} reason={err['msg']}")
        continue

    total_revenue += order.amount
    processed += 1
    print(f"Order {order.order_id}: processed, amount={order.amount}")

print(f"\nDone. Processed: {processed}, Rejected: {failed}, Total revenue: {total_revenue}")
