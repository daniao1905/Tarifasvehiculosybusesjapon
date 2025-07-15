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

# Inicializar session state
if "paradas" not in st.session_state:
    st.session_state.paradas = []

origen = st.text_input("📍 Dirección de origen", placeholder="Ej. Tokyo Station")
sugerencias_origen = place_autocomplete(origen)
if sugerencias_origen:
    origen = st.selectbox("Sugerencias para origen:", sugerencias_origen, key="origen_sug")

# Botón para añadir paradas
st.markdown("### 🛑 Paradas intermedias")
if st.button("➕ Añadir parada"):
    st.session_state.paradas.append("")

# Mostrar campos para paradas intermedias
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

# Selección de horas de servicio (mínimo 3)
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
            total_min = 0
            route_points = []

            for leg in directions[0]['legs']:
                total_km += leg['distance']['value'] / 1000
                total_min += leg['duration']['value'] / 60
                for step in leg['steps']:
                    route_points.append((step['start_location']['lat'], step['start_location']['lng']))
                route_points.append((leg['end_location']['lat'], leg['end_location']['lng']))

            duration_text = f"{int(total_min // 60)}h {int(total_min % 60)}min"
            st.success(f"📏 Distancia total: {total_km:.1f} km | ⏱️ Duración total: {duration_text}")

            tipo_vehiculo = st.selectbox("Tipo de vehículo", ["Hiace", "Alphard", "Microbús", "Bus grande"])

            if tipo_vehiculo in ["Hiace", "Alphard"]:
                base_tarifa = 20000  # nueva base
                extra_blocks = 0
                if total_km > 15:
                    extra_blocks = max(extra_blocks, math.ceil((total_km - 15) / 7.5))
                if total_min > 60:
                    extra_blocks = max(extra_blocks, math.ceil((total_min - 60) / 30))
                extra_cost = extra_blocks * 3480
                retorno_cost = 3500
                total = base_tarifa + extra_cost + retorno_cost

                st.info(f"💴 Tarifa Hiace/Alphard: Base ¥20,000 + Excedente ¥{extra_cost:,} + Retorno ¥3,500")
                st.success(f"🧾 Total estimado: ¥{total:,}")

            else:
                horas_cobradas = max(horas_usuario, 3)
                tarifa_hora = 7000
                tarifa_km = 170
                total = int(horas_cobradas * tarifa_hora + total_km * tarifa_km)

                st.info(f"💴 Tarifa Microbús/Bus grande: {horas_cobradas}h × ¥{tarifa_hora} + {total_km:.1f}km × ¥{tarifa_km}")
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