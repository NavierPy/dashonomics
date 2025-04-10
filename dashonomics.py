import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Dashonomics", layout="wide")
st.title("📊 Dashonomics")
st.markdown("Indicadores económicos clave de España. Datos en tiempo real desde la API oficial de Eurostat.")

# ================================
# 🔧 Conversión de fechas
# ================================

def convertir_fecha_mensual(fecha_str):
    return datetime.strptime(fecha_str, "%YM%m")

def convertir_fecha_trimestral(fecha_str):
    año, trimestre = fecha_str.split("-Q")
    mes = (int(trimestre) - 1) * 3 + 1
    return datetime(int(año), mes, 1)

# ================================
# 📈 Indicadores económicos
# ================================

@st.cache_data
def obtener_pib_trimestral():
    url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/namq_10_pc"
    params = {
        "geo": "ES",
        "unit": "CP_EUR_HAB",
        "na_item": "B1GQ",
        "format": "JSON"
    }
    response = requests.get(url, params=params)
    data = response.json()
    time_labels = {v: k for k, v in data['dimension']['time']['category']['index'].items()}
    valores = []
    for key_str, value in data['value'].items():
        time_idx = int(key_str.split(":")[-1])
        fecha = time_labels.get(time_idx)
        if fecha:
            valores.append((fecha, value))
    df = pd.DataFrame(valores, columns=['Fecha', 'Valor'])
    df["Fecha"] = df["Fecha"].apply(convertir_fecha_trimestral)
    return df.sort_values("Fecha")

@st.cache_data
def obtener_ipc_mensual():
    url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_midx"
    params = {
        "geo": "ES",
        "coicop": "CP00",
        "unit": "I15",
        "format": "JSON"
    }
    response = requests.get(url, params=params)
    data = response.json()
    time_labels = {v: k for k, v in data['dimension']['time']['category']['index'].items()}
    valores = []
    for key_str, value in data['value'].items():
        time_idx = int(key_str.split(":")[-1])
        fecha = time_labels.get(time_idx)
        if fecha:
            valores.append((fecha, value))
    df = pd.DataFrame(valores, columns=['Fecha', 'Valor'])
    df["Fecha"] = df["Fecha"].apply(convertir_fecha_mensual)
    return df.sort_values("Fecha")

@st.cache_data
def obtener_paro_mensual():
    url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/une_rt_m"
    params = {
        "geo": "ES",
        "sex": "T",
        "age": "TOTAL",
        "unit": "PC_ACT",
        "format": "JSON"
    }
    response = requests.get(url, params=params)
    data = response.json()
    time_labels = {v: k for k, v in data['dimension']['time']['category']['index'].items()}
    valores = []
    for key_str, value in data['value'].items():
        time_idx = int(key_str.split(":")[-1])
        fecha = time_labels.get(time_idx)
        if fecha:
            valores.append((fecha, value))
    df = pd.DataFrame(valores, columns=['Fecha', 'Valor'])
    df["Fecha"] = df["Fecha"].apply(convertir_fecha_mensual)
    return df.sort_values("Fecha")

# ================================
# 🎛️ Filtros
# ================================

st.sidebar.title("🎯 Filtros")
rango = st.sidebar.slider("Rango de años", 2015, 2025, (2018, 2024))

# ================================
# 📊 Visualización
# ================================

def mostrar_serie(nombre, df):
    df_filtrado = df[df['Fecha'].dt.year.between(rango[0], rango[1])]
    fig = px.line(df_filtrado, x='Fecha', y='Valor', title=nombre, markers=True)
    fig.update_layout(height=350, margin=dict(t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 PIB per cápita (trimestral)")
    mostrar_serie("PIB per cápita [€]", obtener_pib_trimestral())

with col2:
    st.subheader("📉 Tasa de paro (mensual)")
    mostrar_serie("Paro (%)", obtener_paro_mensual())

st.subheader("🛒 IPC (mensual)")
mostrar_serie("Índice de Precios al Consumo (base 2015)", obtener_ipc_mensual())

st.markdown("---")
st.caption("📡 Fuente: Eurostat REST API | Datos actualizados automáticamente")
