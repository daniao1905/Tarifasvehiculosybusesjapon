import streamlit as st
import googlemaps
from streamlit_folium import st_folium
import folium
import os

st.set_page_config(page_title="Tarifas de Vehículos y Buses en Japón", layout="wide")

st.title("TARIFAS DE VEHÍCULOS Y BUSES EN JAPÓN")

# Configuración de la API Key
api_key = st.secrets["GOOGLE_MAPS_API_KEY"]
gmaps = googlemaps.Client(key=api_key)

st.markdown("### Ingrese Origen y Destino para calcular el recorrido y la tarifa")
col1, col2 = st.columns(2)

with col1:
    origen = st.text_input("📍 Dirección de origen", placeholder="Ej. Tokyo Station")
with col2:
    destino = st.text_input("🏁 Dirección de destino", placeholder="Ej. Kyoto Station")

if origen and destino:
    # Calcular distancia y ruta
    directions = gmaps.directions(origen, destino, mode="driving", language="ja")

    if directions:
        distance_text = directions[0]['legs'][0]['distance']['text']
        distance_km = directions[0]['legs'][0]['distance']['value'] / 1000
        duration = directions[0]['legs'][0]['duration']['text']
        start_location = directions[0]['legs'][0]['start_location']
        end_location = directions[0]['legs'][0]['end_location']

        st.success(f"📏 Distancia: {distance_text} | ⏱️ Duración estimada: {duration}")

        st.markdown("### Seleccione el tipo de vehículo")
        tipo_vehiculo = st.selectbox("Tipo de vehículo", ["Hiace", "Alphard", "Microbús", "Bus grande"])

        tarifas_base = {
            "Hiace": 15000,
            "Alphard": 18000,
            "Microbús": 25000,
            "Bus grande": 35000,
        }

        tarifa_total = tarifas_base[tipo_vehiculo]
        st.info(f"💴 Tarifa mínima por 3 horas ({tipo_vehiculo}): ¥{tarifa_total:,}")

        st.markdown("### 🗺️ Mapa del recorrido")
        mapa = folium.Map(location=[(start_location['lat'] + end_location['lat']) / 2,
                                    (start_location['lng'] + end_location['lng']) / 2], zoom_start=6)
        folium.Marker([start_location['lat'], start_location['lng']], tooltip="Origen").add_to(mapa)
        folium.Marker([end_location['lat'], end_location['lng']], tooltip="Destino").add_to(mapa)
        folium.PolyLine(
            locations=[(step['start_location']['lat'], step['start_location']['lng']) for step in directions[0]['legs'][0]['steps']],
            color="blue"
        ).add_to(mapa)
        st_folium(mapa, width=1000, height=500)
    else:
        st.error("No se pudo calcular la ruta. Verifique las direcciones.")