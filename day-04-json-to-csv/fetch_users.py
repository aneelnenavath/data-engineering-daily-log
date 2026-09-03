import requests
import pandas as pd

URL = "https://jsonplaceholder.typicode.com/users"

def fetch_users(url):
    response = requests.get(url)
    print(f"GET {url} -> status {response.status_code}")
    response.raise_for_status()
    return response.json()

def flatten_and_save(data, output_path):
    df = pd.json_normalize(data)
    df.to_csv(output_path, index=False)
    print(f"Wrote {len(df)} rows and {len(df.columns)} columns to {output_path}")

if __name__ == "__main__":
    data = fetch_users(URL)
    flatten_and_save(data, "users.csv")
