import great_expectations as gx
import pandas as pd

context = gx.get_context(mode="ephemeral")

df = pd.read_csv("seeds/raw_orders.csv")

data_source = context.data_sources.add_pandas("orders_datasource")
data_asset = data_source.add_dataframe_asset(name="orders_asset")
batch_definition = data_asset.add_batch_definition_whole_dataframe("orders_batch")
batch = batch_definition.get_batch(batch_parameters={"dataframe": df})

suite = context.suites.add(gx.ExpectationSuite(name="orders_suite"))

suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="customer_id"))
suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="amount"))
suite.add_expectation(gx.expectations.ExpectColumnValuesToBeUnique(column="order_id"))
suite.add_expectation(gx.expectations.ExpectColumnValuesToBeInSet(column="status", value_set=["completed", "pending", "cancelled"]))
suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(column="amount", min_value=0))

results = batch.validate(suite)

print("SUCCESS:", results["success"])
for r in results["results"]:
    exp_type = r["expectation_config"]["type"]
    exp_kwargs = r["expectation_config"]["kwargs"]
    print(f"  {exp_type} {exp_kwargs} -> success={r['success']}")
    if not r["success"]:
        unexpected = r["result"].get("partial_unexpected_list")
        count = r["result"].get("unexpected_count")
        print(f"    FAILING VALUES: {unexpected} (unexpected_count={count})")
