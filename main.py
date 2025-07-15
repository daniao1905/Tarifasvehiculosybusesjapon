
import streamlit as st
from utils import calcular_tarifa, get_kilometros_google
from scraper import obtener_tarifas

st.set_page_config(page_title="Tarifas MK Osaka", layout="centered")

st.title("Calculadora de Tarifas MK Group (Osaka)")

vehiculo = st.selectbox("Tipo de Vehículo", ["sedan", "alphard", "hiace", "bus"])

origen = st.text_input("Lugar de recogida (Google Maps)")
destino = st.text_input("Destino (Google Maps)")
horas = st.number_input("Horas de reserva", min_value=1.0, step=0.5)

kilometros = 0
if vehiculo == "bus" and origen and destino:
    try:
        kilometros = get_kilometros_google(origen, destino)
        st.success(f"Distancia estimada: {kilometros} km")
    except:
        st.warning("No se pudo calcular la distancia con Google Maps.")

if st.button("Calcular tarifa"):
    tarifas = obtener_tarifas()
    total = calcular_tarifa(vehiculo, horas, kilometros, tarifas)
    st.subheader(f"Tarifa total estimada: ¥{total:,}")
