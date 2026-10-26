import pytest

from transform import normalize_order


def test_normalizes_a_clean_record():
    result = normalize_order({"order_id": 1, "status": "completed", "amount": 50.0})
    assert result == {
        "order_id": 1,
        "status": "completed",
        "amount": 50.0,
        "amount_with_tax": 60.0,
    }


def test_strips_and_lowercases_status():
    result = normalize_order({"order_id": 2, "status": "  PENDING  ", "amount": 10.0})
    assert result["status"] == "pending"


def test_converts_string_amount_to_float():
    result = normalize_order({"order_id": 3, "status": "completed", "amount": "25.50"})
    assert result["amount"] == 25.50
    assert isinstance(result["amount"], float)


def test_computes_tax_inclusive_total_correctly():
    result = normalize_order({"order_id": 4, "status": "completed", "amount": 100.0})
    assert result["amount_with_tax"] == 120.0


def test_zero_amount_is_allowed():
    result = normalize_order({"order_id": 5, "status": "completed", "amount": 0.0})
    assert result["amount"] == 0.0
    assert result["amount_with_tax"] == 0.0


def test_rejects_invalid_status():
    with pytest.raises(ValueError, match="invalid status"):
        normalize_order({"order_id": 6, "status": "refunded", "amount": 10.0})


def test_rejects_negative_amount():
    with pytest.raises(ValueError, match="amount cannot be negative"):
        normalize_order({"order_id": 7, "status": "completed", "amount": -5.0})
