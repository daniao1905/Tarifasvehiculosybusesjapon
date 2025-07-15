# TARIFAS DE VEHÍCULOS Y BUSES EN JAPÓN

Aplicación en Streamlit para calcular rutas, distancia y tarifas mínimas para vehículos turísticos en Japón.

## Características

- Mapa con ruta entre dos puntos usando Google Maps.
- Cálculo de distancia y duración.
- Tarifa mínima automática (3 horas).
- Visualización en mapa interactivo.

## Cómo usar

1. Clona este repositorio.
2. Crea un archivo `.streamlit/secrets.toml` con tu API Key de Google Maps.
3. Ejecuta:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```