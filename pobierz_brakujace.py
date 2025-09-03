import requests
import csv

# Wczytaj brakujące ID z pliku
with open("missing_ids.txt", "r") as f:
    missing = f.read().strip().split(",")

# Nazwy kolumn, które chcemy
fields = ["id", "name", "slug", "rank", "active", "banned", "is_admin", "is_moderator"]

with open("profiles.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()

    for user_id in missing:
        url = f"https://jbzd.com.pl/user/profile/{user_id}"
        print(f"Pobieram: {url}")

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "success" and "user" in data:
                user = data["user"]

                # wybieramy tylko potrzebne pola
                row = {field: user.get(field) for field in fields}
                writer.writerow(row)

            else:
                print(f"Brak danych dla ID {user_id}")

        except Exception as e:
            print(f"Błąd przy {url}: {e}")

print("Zapisano wyniki do profiles.csv")
