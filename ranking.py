import requests
import csv
import time

# --- KONFIGURACJA ---
total_pages = 100  # testowo
url_template = "https://api.jbzd.com.pl/ranking/get?page={}&per_page=50"

results = []
status_counter = {"200": 0, "404": 0, "other": 0}
start_time = time.time()

for page in range(1, total_pages + 1):
    try:
        response = requests.get(url_template.format(page))
        status = str(response.status_code)

        if status == "200":
            status_counter["200"] += 1
            data = response.json().get("rankings", {}).get("data", [])
            for user in data:
                results.append({
                    "id": user["id"],
                    "points": user["points"],
                    "rank": user["rank"],
                    "name": user["model"]["name"],
                    "slug": user["model"]["slug"],
                    "color": user["model"]["color"]
                })
        elif status == "404":
            status_counter["404"] += 1
        else:
            status_counter["other"] += 1

    except Exception as e:
        status_counter["other"] += 1

    # Szacowanie ETA
    elapsed = time.time() - start_time
    avg_time = elapsed / page
    remaining = avg_time * (total_pages - page)
    eta_h = int(remaining // 3600)
    eta_m = int((remaining % 3600) // 60)
    eta_s = int(remaining % 60)

    if page % 10 == 0:  # wypisuj co 10 stron
        print(f"Strona {page}/{total_pages} | Statusy: {status_counter} | ETA: {eta_h:02d}:{eta_m:02d}:{eta_s:02d}", flush=True)

# --- SORTOWANIE PO ID ---
results_sorted = sorted(results, key=lambda x: x["id"])

# --- ZAPIS DO CSV ---
csv_file = "ranking_100.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "points", "rank", "name", "slug", "color"])
    writer.writeheader()
    for row in results_sorted:
        writer.writerow(row)

print(f"\nPobrano {len(results_sorted)} rekordów. Plik '{csv_file}' zapisany.", flush=True)
