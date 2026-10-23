from mock_api import MockOrdersAPI

api = MockOrdersAPI()

response = api.get_page()
records = response["records"]

print(f"Fetched {len(records)} records.")
print(f"API calls made: {api.call_count}")
print("Done - assuming this is all the data.")
