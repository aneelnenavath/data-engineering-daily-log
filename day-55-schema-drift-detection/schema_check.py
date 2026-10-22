REFERENCE_SCHEMA = {
    "order_id": int,
    "customer_id": int,
    "status": str,
    "amount": float,
    "order_date": str,
}


def infer_type(value):
    if isinstance(value, bool):
        return bool
    if isinstance(value, int):
        return int
    if isinstance(value, float):
        return float
    if isinstance(value, str):
        return str
    return type(value)


def diff_schema(reference_schema, rows):
    """Compare the actual columns/types seen in a batch of rows against
    a reference schema. Returns new columns, missing columns, and any
    column whose type disagrees with the reference."""
    if not rows:
        return {"new_columns": [], "missing_columns": [], "type_changes": []}

    actual_columns = set()
    observed_types = {}
    for row in rows:
        for key, value in row.items():
            actual_columns.add(key)
            if value is not None:
                observed_types.setdefault(key, infer_type(value))

    reference_columns = set(reference_schema.keys())

    new_columns = sorted(actual_columns - reference_columns)
    missing_columns = sorted(reference_columns - actual_columns)

    type_changes = []
    for col in sorted(actual_columns & reference_columns):
        expected = reference_schema[col]
        actual = observed_types.get(col)
        if actual is not None and actual is not expected:
            type_changes.append((col, expected.__name__, actual.__name__))

    return {
        "new_columns": new_columns,
        "missing_columns": missing_columns,
        "type_changes": type_changes,
    }
