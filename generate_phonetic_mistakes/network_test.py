import requests

url = "https://archive.org/services/openlibrary/people/malumuscho/lists/OL157287L/seeds.json"

response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
print(response.status_code)
print(response.text[:200])
