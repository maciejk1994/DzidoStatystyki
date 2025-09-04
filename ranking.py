import requests
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque

# --- KONFIGURACJA ---
BLOCK_SIZE = 1000        # liczba stron w jednym bloku
PER_PAGE = 50            # liczba wpisów na stronę
THREADS = 10             # liczba równoległych wątków

url_template = "https://api.jbzd.com.pl/ranking/get?page={}&per_page={}"

# --- FUNKCJE ---
def fetch_page(page):
    """Pobiera pojedynczą stronę."""
    try:
        resp = requests.get(url_template.format(page, PER_PAGE), timeout=10)
        if resp.status_code == 200:
            data = resp.json().get("rankings", {}).get("data", [])
            return "ok", data
        elif resp.status_code == 404:
            print(f"Strona {page} nie istnieje (404), pomijamy", flush=True)
            return "skip", []
        else:
            return "retry", []
    except Exception:
        return "retry", []

def fetch_block(start_page, end_page):
    """Pobiera blok stron z retry dla błędów innych niż 404."""
    results = []
    pages_queue = deque(range(start_page, end_page + 1))
    
    while pages_queue:
        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            futures = {executor.submit(fetch_page, page): page for page in list(pages_queue)}
            pages_queue.clear()
            
            for future in as_completed(futures):
                page = futures[future]
                status, data = future.result()
                
                if status == "ok":
                    results.extend([{
                        "id": u["id"],
                        "points": u["points"],
                        "rank": u["rank"],
                        "name": u["model"]["name"],
                        "slug": u["model"]["slug"],
                        "color": u["model"]["color"]
                    } for u in data])
                    print(f"Pobrano stronę {page}", flush=True)
                elif status == "retry":
                    pages_queue.append(page)
                    print(f"Strona {page} nieudana – wraca na koniec kolejki", flush=True)
                elif status == "skip":
                    continue
        
        if pages_queue:
            time.sleep(5)
    
    return results

# --- GŁÓWNY SKRYPT ---
all_results = []
start_time = time.time()

# Pobieramy pierwszą stronę, aby określić ile jest wszystkich stron
resp = requests.get(url_template.format(1, PER_PAGE)).json()
last_page = resp.get("rankings", {}).get("last_page", 1)
print(f"Łączna liczba stron do pobrania: {last_page}")

for block_start in range(1, last_page + 1, BLOCK_SIZE):
    block_end = min(block_start + BLOCK_SIZE - 1, last_page)
    print(f"\n--- Pobieranie blok {block_start}-{block_end} ---", flush=True)
    
    block_results = fetch_block(block_start, block_end)
    all_results.extend(block_results)

    # Sortowanie po id
    all_results_sorted = sorted(all_results, key=lambda x: x["id"])

    # Zapis do CSV po każdym bloku
    csv_file = "ranking.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "points", "rank", "name", "slug", "color"])
        writer.writeheader()
        for row in all_results_sorted:
            writer.writerow(row)

    print(f"Blok {block_start}-{block_end} zapisany do {csv_file} (łącznie {len(all_results_sorted)} rekordów)", flush=True)

end_time = time.time()
print(f"\nCałkowity czas pobierania: {end_time - start_time:.2f} sekund")
