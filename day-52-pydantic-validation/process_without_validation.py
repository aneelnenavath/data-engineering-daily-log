from raw_orders import RAW_ORDERS

print("Processing orders without validation...\n")

total_revenue = 0
processed = 0

for order in RAW_ORDERS:
    total_revenue += order["amount"]
    processed += 1
    print(f"Order {order['order_id']}: processed, amount={order['amount']}")

print(f"\nDone. Processed: {processed}, Total revenue: {total_revenue}")
