from airflow.decorators import dag, task
from datetime import datetime
import csv
import os

DATA_DIR = "/opt/airflow/data/regions"

REGIONS = {
    "north": [(1, 50.0), (2, 30.0), (3, 20.0)],             # 100.0
    "south": [(4, 15.0), (5, 25.0)],                         # 40.0
    "east":  [(6, 10.0), (7, 10.0), (8, 10.0), (9, 10.0)],   # 40.0
    "west":  [(10, 5.0), (11, 5.0)],                         # 10.0
}


@dag(dag_id="day24_dynamic_mapping", start_date=datetime(2026, 1, 1), schedule=None, catchup=False)
def day24_dynamic_mapping():

    @task
    def generate_regional_files():
        os.makedirs(DATA_DIR, exist_ok=True)
        paths = []
        for region, rows in REGIONS.items():
            path = os.path.join(DATA_DIR, f"{region}.csv")
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["order_id", "amount"])
                for oid, amt in rows:
                    writer.writerow([oid, amt])
            paths.append(path)
        return paths

    @task
    def process_file(file_path: str):
        total = 0.0
        with open(file_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                total += float(row["amount"])
        region = os.path.basename(file_path).replace(".csv", "")
        summary_path = f"/opt/airflow/data/regions/{region}_summary.txt"
        with open(summary_path, "w") as f:
            f.write(f"region={region},total={total}\n")
        print(f"Region {region}: total {total}")
        return {"region": region, "total": total}

    @task
    def aggregate_totals(results: list):
        grand_total = sum(r["total"] for r in results)
        with open(f"{DATA_DIR}/grand_total.txt", "w") as f:
            f.write(f"grand_total={grand_total}\n")
        print(f"Per-region results: {results}")
        print(f"Grand total: {grand_total}")
        return grand_total

    file_paths = generate_regional_files()
    results = process_file.expand(file_path=file_paths)
    aggregate_totals(results)


day24_dynamic_mapping()
