# TARIFAS DE VEHÍCULOS Y BUSES EN JAPÓN

Aplicación en Streamlit para calcular rutas, distancia y tarifas mínimas para transporte turístico en Japón.

## APIs necesarias en Google Cloud
- Maps JavaScript API
- Places API
- Directions API

## Cómo usar

1. Clona este repositorio o súbelo a Streamlit Cloud.
2. En los Secrets agrega:

```
GOOGLE_MAPS_API_KEY = "tu_api_key"
```

3. Ejecuta:

```bash
pip install -r requirements.txt
streamlit run main.py
```