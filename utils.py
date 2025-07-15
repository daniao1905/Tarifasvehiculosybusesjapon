
import math
import googlemaps

API_KEY = "AIzaSyAqr6wh2zOZwHHAR5-DXPPtL1av87K1V_U"

def calcular_tarifa(vehiculo, horas, kilometros, tarifas):
    if vehiculo == "sedan":
        return int(tarifas["sedan"] * horas)
    elif vehiculo in ["alphard", "hiace"]:
        base = 15790
        adicionales = max(0, math.ceil((horas - 1) * 2))  # cada 30 min = 0.5h
        return base + (adicionales * 3480)
    elif vehiculo == "bus":
        return int(horas * 7000 + kilometros * 170)
    else:
        return 0

def get_kilometros_google(origen, destino):
    gmaps = googlemaps.Client(key=API_KEY)
    result = gmaps.distance_matrix(origen, destino, mode="driving")
    distancia_metros = result["rows"][0]["elements"][0]["distance"]["value"]
    return round(distancia_metros / 1000)
