import csv
import json
import logging

ALLOWED_STATUSES = {"completed", "pending", "cancelled"}


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "job": "order_batch_processor",
            "message": record.getMessage(),
        }
        if hasattr(record, "row_id"):
            payload["row_id"] = record.row_id
        if hasattr(record, "reason"):
            payload["reason"] = record.reason
        return json.dumps(payload)


logger = logging.getLogger("order_batch_processor")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)

logger.info("Starting order batch processing")

processed = 0
failed = 0

with open("orders_batch.csv") as f:
    for row in csv.DictReader(f):
        row_id = row["row_id"]

        if not row["customer_id"].strip():
            logger.error("Row failed validation", extra={"row_id": row_id, "reason": "missing_customer_id"})
            failed += 1
            continue

        try:
            amount = float(row["amount"])
        except ValueError:
            logger.error("Row failed validation", extra={"row_id": row_id, "reason": f"amount_not_numeric:{row['amount']}"})
            failed += 1
            continue

        if amount < 0:
            logger.error("Row failed validation", extra={"row_id": row_id, "reason": f"negative_amount:{amount}"})
            failed += 1
            continue

        if row["status"] not in ALLOWED_STATUSES:
            logger.error("Row failed validation", extra={"row_id": row_id, "reason": f"invalid_status:{row['status']}"})
            failed += 1
            continue

        logger.info("Row processed", extra={"row_id": row_id})
        processed += 1

logger.info("Batch complete", extra={"reason": f"processed={processed},failed={failed}"})
