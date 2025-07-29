# app_creator/cli.py

import requests

def get_location():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        print(f"IP: {data.get('ip')}")
        print(f"Ville: {data.get('city')}")
        print(f"Région: {data.get('region')}")
        print(f"Pays: {data.get('country')}")
        print(f"Localisation (lat,long): {data.get('loc')}")
        print(f"Fournisseur: {data.get('org')}")
    except Exception as e:
        print(f"Erreur lors de la récupération de la localisation: {e}")

if __name__ == "__main__":
    get_location()
