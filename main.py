import streamlit as st
import googlemaps
from streamlit_folium import st_folium
import folium
import math

st.set_page_config(page_title="Tarifas de Vehículos y Buses en Japón", layout="wide")
st.title("TARIFAS DE VEHÍCULOS Y BUSES EN JAPÓN")

api_key = st.secrets.get("GOOGLE_MAPS_API_KEY", None)
if not api_key:
    st.error("❌ Falta la API Key de Google Maps. Agrega tu clave en los Secrets.")
    st.stop()

gmaps = googlemaps.Client(key=api_key)

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
            distance_km = leg['distance']['value'] / 1000
            duration_min = leg['duration']['value'] / 60
            duration_text = leg['duration']['text']
            distance_text = leg['distance']['text']

            start_location = leg['start_location']
            end_location = leg['end_location']

            st.success(f"📏 Distancia: {distance_text} | ⏱️ Duración estimada: {duration_text}")

            tipo_vehiculo = st.selectbox("Tipo de vehículo", ["Hiace", "Alphard", "Microbús", "Bus grande"])

            if tipo_vehiculo in ["Hiace", "Alphard"]:
                base_tarifa = 20,000
                extra_blocks = 0

                if distance_km > 15:
                    extra_blocks = max(extra_blocks, math.ceil((distance_km - 15) / 7.5))
                if duration_min > 60:
                    extra_blocks = max(extra_blocks, math.ceil((duration_min - 60) / 30))

                extra_cost = extra_blocks * 3480
                retorno_cost = 3500  # asumido fijo

                total = base_tarifa + extra_cost + retorno_cost

                st.info(f"💴 Tarifa Hiace/Alphard: Base ¥20,000 + Excedente ¥{extra_cost:,} + Retorno ¥3,500")
                st.success(f"🧾 Total estimado: ¥{total:,}")

            else:
                horas_cobradas = max(round(duration_min / 60, 1), 3)
                tarifa_hora = 7000
                tarifa_km = 170
                total = int(horas_cobradas * tarifa_hora + distance_km * tarifa_km)

                st.info(f"💴 Tarifa Microbús/Bus grande: {horas_cobradas}h × ¥{tarifa_hora} + {distance_km:.1f}km × ¥{tarifa_km}")
                st.success(f"🧾 Total estimado: ¥{total:,}")

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
