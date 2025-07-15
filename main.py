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

if "paradas" not in st.session_state:
    st.session_state.paradas = []

origen = st.text_input("📍 Dirección de origen", placeholder="Ej. Tokyo Station")
sugerencias_origen = place_autocomplete(origen)
if sugerencias_origen:
    origen = st.selectbox("Sugerencias para origen:", sugerencias_origen, key="origen_sug")

st.markdown("### 🛑 Paradas intermedias")
if st.button("➕ Añadir parada"):
    st.session_state.paradas.append("")

paradas = []
for i, parada_actual in enumerate(st.session_state.paradas):
    parada_input = st.text_input(f"Parada {i+1}", value=parada_actual, key=f"parada_{i}")
    sugerencias = place_autocomplete(parada_input)
    if sugerencias:
        seleccion = st.selectbox(f"Sugerencias para Parada {i+1}", sugerencias, key=f"sug_parada_{i}")
        paradas.append(seleccion)
    else:
        paradas.append(parada_input)

destino = st.text_input("🏁 Dirección de destino final", placeholder="Ej. Kyoto Station")
sugerencias_destino = place_autocomplete(destino)
if sugerencias_destino:
    destino = st.selectbox("Sugerencias para destino final:", sugerencias_destino, key="destino_sug")

# Ingreso manual de horas (mínimo 3)
horas_usuario = st.number_input("🕒 Horas de servicio (mínimo 3)", min_value=3.0, value=3.0, step=0.5)

if origen and destino:
    try:
        directions = gmaps.directions(
            origin=origen,
            destination=destino,
            waypoints=paradas,
            mode="driving",
            language="ja"
        )

        if directions:
            total_km = 0
            route_points = []

            for leg in directions[0]['legs']:
                total_km += leg['distance']['value'] / 1000
                for step in leg['steps']:
                    route_points.append((step['start_location']['lat'], step['start_location']['lng']))
                route_points.append((leg['end_location']['lat'], leg['end_location']['lng']))

            st.success(f"📏 Distancia total: {total_km:.1f} km | ⏱️ Horas seleccionadas por el cliente: {horas_usuario}h")

            tipo_vehiculo = st.selectbox("Tipo de vehículo", ["Hiace", "Alphard", "Microbús", "Bus grande"])

            if tipo_vehiculo in ["Hiace", "Alphard"]:
                base_tarifa = 20000
                km_extras = max(0, total_km - 15)
                horas_extras = max(0, horas_usuario - 3)
                bloques_km = math.ceil(km_extras / 7.5)
                bloques_tiempo = math.ceil(horas_extras)
                bloques_cobrables = max(bloques_km, bloques_tiempo)
                extra_cost = bloques_cobrables * 3500
                retorno_cost = 3500
                total = base_tarifa + extra_cost + retorno_cost

                st.info(f"💴 Base ¥20,000 + {bloques_cobrables} bloques × ¥3,500 = ¥{extra_cost:,} + Retorno ¥3,500")
                st.success(f"🧾 Total estimado: ¥{total:,}")

            else:
                tarifa_hora = 7000
                tarifa_km = 170
                total = int(horas_usuario * tarifa_hora + total_km * tarifa_km)

                st.info(f"💴 {horas_usuario}h × ¥{tarifa_hora} + {total_km:.1f}km × ¥{tarifa_km}")
                st.success(f"🧾 Total estimado: ¥{total:,}")

            st.markdown("### 🗺️ Mapa del recorrido")
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