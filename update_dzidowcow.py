import requests
import csv

CSV_FILE = "lista_dzidowcow.csv"
BATCH_SIZE = 100

# Nazwy kolumn
fields = ["id","name","slug","rank","active","banned","is_admin","is_moderator"]

# Znajdź ostatnie ID w pliku
try:
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        ids = [int(row["id"]) for row in reader]
        last_id = max(ids) if ids else 0
except FileNotFoundError:
    last_id = 0

start_id = last_id + 1
end_id = start_id + BATCH_SIZE - 1

print(f"Pobieram profile ID od {start_id} do {end_id}...")

with open(CSV_FILE, "a", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    
    # jeśli plik nie istnieje lub jest pusty, zapisz nagłówek
    if last_id == 0:
        writer.writeheader()

    for user_id in range(start_id, end_id + 1):
        url = f"https://jbzd.com.pl/user/profile/{user_id}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "success" and "user" in data:
                user = data["user"]
                row = {field: user.get(field) for field in fields}
                writer.writerow(row)
                print(f"Dodano ID {user_id}")
            else:
                print(f"ID {user_id} nie istnieje")

        except Exception as e:
            print(f"Błąd przy ID {user_id}: {e}")

print("Gotowe!")
