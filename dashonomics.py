import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Dashonomics", layout="wide")
st.title("📊 Dashonomics")
st.markdown("Indicadores económicos actualizados en tiempo real desde la API oficial de Eurostat.")

# ================================
# 🔧 Utilidad para cargar y parsear datos Eurostat
# ================================

def cargar_datos_eurostat(dataset_id, filtros):
    base_url = f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset_id}"
    filtros['format'] = 'JSON'
    response = requests.get(base_url, params=filtros)
    if response.status_code != 200:
        raise ValueError(f"Error {response.status_code} al obtener datos de Eurostat")

    data = response.json()
    dimensiones = data['dimension']
    time = dimensiones['time']['category']['index']
    valores = data['value']

    # Mapeamos índice temporal a año
    tiempo = pd.Series(time).sort_values().index
    df = pd.DataFrame({'Año': [int(t) for t in tiempo], 'Valor': list(valores.values())})
    return df

# ================================
# 📈 Indicadores
# ================================

@st.cache_data
def obtener_pib():
    return cargar_datos_eurostat("nama_10_pc", {
        "geo": "ES",
        "unit": "CP_EUR_HAB"
    })

@st.cache_data
def obtener_paro():
    df = cargar_datos_eurostat("une_rt_m", {
        "geo": "ES",
        "sex": "T",
        "age": "Y15-74",
        "unit": "PC_ACT"
    })
    # Hay un valor por mes: agregamos por año
    df['Año'] = df['Año'].astype(str).str[:4].astype(int)
    return df.groupby('Año')['Valor'].mean().reset_index()

@st.cache_data
def obtener_ipc():
    df = cargar_datos_eurostat("prc_hicp_midx", {
        "geo": "ES",
        "coicop": "CP00",
        "unit": "INX",
        "indic": "IDX"
    })
    df['Año'] = df['Año'].astype(str).str[:4].astype(int)
    return df.groupby('Año')['Valor'].mean().reset_index()

# ================================
# 🎛️ Filtros y visualización
# ================================

st.sidebar.title("🎯 Filtros")
rango = st.sidebar.slider("Selecciona rango de años", 2000, 2025, (2015, 2023))

def mostrar_indicador(nombre, df):
    df_filtrado = df[(df['Año'] >= rango[0]) & (df['Año'] <= rango[1])]
    fig = px.line(df_filtrado, x='Año', y='Valor', markers=True, title=nombre)
    fig.update_layout(margin=dict(t=30, b=20), height=350)
    st.plotly_chart(fig, use_container_width=True)

# ================================
# 📊 Renderización de indicadores
# ================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 PIB per cápita (€)")
    mostrar_indicador("PIB per cápita (CP_EUR_HAB)", obtener_pib())

with col2:
    st.subheader("📉 Tasa de paro (%)")
    mostrar_indicador("Tasa de paro (promedio anual)", obtener_paro())

st.subheader("🛒 Índice de Precios al Consumo (IPC)")
mostrar_indicador("IPC promedio anual (base 2015 = 100)", obtener_ipc())

st.markdown("---")
st.caption("📡 Fuente: Eurostat REST API (https://ec.europa.eu/eurostat)")
