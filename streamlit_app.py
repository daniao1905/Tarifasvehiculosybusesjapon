import streamlit as st
import googlemaps
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="Tarifas de Vehículos y Buses en Japón", layout="wide")
st.title("TARIFAS DE VEHÍCULOS Y BUSES EN JAPÓN")

# Obtener la API Key desde secrets
api_key = st.secrets.get("GOOGLE_MAPS_API_KEY", None)
if not api_key:
    st.error("❌ Falta la API Key de Google Maps. Agrega tu clave en los Secrets.")
    st.stop()

gmaps = googlemaps.Client(key=api_key)

st.markdown("### Ingrese Origen y Destino para calcular el recorrido y la tarifa")
col1, col2 = st.columns(2)

with col1:
    origen = st.text_input("📍 Dirección de origen", placeholder="Ej. Tokyo Station")
with col2:
    destino = st.text_input("🏁 Dirección de destino", placeholder="Ej. Kyoto Station")

if origen and destino:
    try:
        directions = gmaps.directions(origen, destino, mode="driving", language="ja")

        if directions:
            leg = directions[0]['legs'][0]
            distance_text = leg['distance']['text']
            distance_km = leg['distance']['value'] / 1000
            duration = leg['duration']['text']
            start_location = leg['start_location']
            end_location = leg['end_location']

            st.success(f"📏 Distancia: {distance_text} | ⏱️ Duración estimada: {duration}")

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

            ruta = [(step['start_location']['lat'], step['start_location']['lng']) for step in leg['steps']]
            ruta.append((end_location['lat'], end_location['lng']))
            folium.PolyLine(locations=ruta, color="blue").add_to(mapa)

            st_folium(mapa, width=1000, height=500)
        else:
            st.error("No se pudo calcular la ruta. Verifique las direcciones.")
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")