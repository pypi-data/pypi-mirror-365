# app_creator/views.py

import requests
from django.http import JsonResponse

def get_location_view(request):
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        return JsonResponse({
            "ip": data.get("ip"),
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "loc": data.get("loc"),
            "org": data.get("org"),
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
