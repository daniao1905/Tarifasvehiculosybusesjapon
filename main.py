import streamlit as st
import googlemaps
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="Tarifas de Vehículos y Buses en Japón", layout="wide")
st.title("TARIFAS DE VEHÍCULOS Y BUSES EN JAPÓN")

# API Key desde los secrets
api_key = st.secrets.get("GOOGLE_MAPS_API_KEY", None)
if not api_key:
    st.error("❌ Falta la API Key de Google Maps. Agrega tu clave en los Secrets.")
    st.stop()

gmaps = googlemaps.Client(key=api_key)

# Autocompletado usando streamlit autocomplete
def place_autocomplete(input_text):
    if not input_text:
        return []
    predictions = gmaps.places_autocomplete(input_text)
    return [p['description'] for p in predictions]

origen = st.text_input("📍 Dirección de origen", placeholder="Ej. Tokyo Station")
sugerencias_origen = place_autocomplete(origen)
if sugerencias_origen:
    origen = st.selectbox("Sugerencias para origen:", sugerencias_origen)

destino = st.text_input("🏁 Dirección de destino", placeholder="Ej. Kyoto Station")
sugerencias_destino = place_autocomplete(destino)
if sugerencias_destino:
    destino = st.selectbox("Sugerencias para destino:", sugerencias_destino)

if origen and destino:
    try:
        directions = gmaps.directions(origen, destino, mode="driving", language="ja")
        if directions:
            leg = directions[0]['legs'][0]
            distance_text = leg['distance']['text']
            distance_km = leg['distance']['value'] / 1000
            duration_text = leg['duration']['text']
            duration_seconds = leg['duration']['value']
            hours = round(duration_seconds / 3600, 1)
            billed_hours = max(hours, 3)

            start_location = leg['start_location']
            end_location = leg['end_location']

            st.success(f"📏 Distancia: {distance_text} | ⏱️ Duración estimada: {duration_text} | 🧾 Se cobrará por: {billed_hours} horas")

            tipo_vehiculo = st.selectbox("Tipo de vehículo", ["Hiace", "Alphard", "Microbús", "Bus grande"])
            tarifas = {
                "Hiace": {"hora": 7000, "km": 170},
                "Alphard": {"hora": 7000, "km": 170},
                "Microbús": {"hora": 7000, "km": 170},
                "Bus grande": {"hora": 7000, "km": 170},
            }

            t = tarifas[tipo_vehiculo]
            tarifa_total = (billed_hours * t["hora"]) + (distance_km * t["km"])
            st.info(f"💴 Tarifa total estimada: ¥{int(tarifa_total):,} (¥{t['hora']}/h + ¥{t['km']}/km)")

            st.markdown("### 🗺️ Mapa del recorrido")

            route_points = [(step['start_location']['lat'], step['start_location']['lng']) for step in leg['steps']]
            route_points.append((end_location['lat'], end_location['lng']))

            mapa = folium.Map(zoom_start=6)
            mapa.fit_bounds([route_points[0], route_points[-1]])
            folium.Marker(route_points[0], tooltip="Origen").add_to(mapa)
            folium.Marker(route_points[-1], tooltip="Destino").add_to(mapa)
            folium.PolyLine(route_points, color="blue").add_to(mapa)
            st_folium(mapa, width=1000, height=500)
        else:
            st.error("No se pudo calcular la ruta.")
    except Exception as e:
        st.error(f"Error: {e}")