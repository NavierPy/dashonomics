import streamlit as st
import pandas as pd
import plotly.express as px
from eurostatapiclient import EurostatAPIClient

st.set_page_config(page_title="Dashonomics", layout="wide")
st.title("📊 Dashonomics")
st.markdown("Visualiza en tiempo real los principales indicadores económicos de España, directamente desde Eurostat.")

client = EurostatAPIClient()

# === Funciones ===

@st.cache_data
def obtener_pib():
    df = client.get_data('nama_10_pc', flags={'geo': 'ES', 'unit': 'CP_EUR_HAB'})
    df['time'] = df['time'].astype(int)
    df = df[df['time'] >= 2015]
    return df.rename(columns={'time': 'Año', 'value': 'Valor'})[['Año', 'Valor']]

@st.cache_data
def obtener_paro():
    df = client.get_data('une_rt_m', flags={'geo': 'ES', 'sex': 'T', 'age': 'Y15-74', 'unit': 'PC_ACT'})
    df['Año'] = df['time'].str[:4].astype(int)
    df = df[df['Año'] >= 2015]
    return df.groupby('Año')['value'].mean().reset_index().rename(columns={'value': 'Valor'})

@st.cache_data
def obtener_ipc():
    df = client.get_data('prc_hicp_midx', flags={'geo': 'ES', 'coicop': 'CP00', 'unit': 'INX', 'indic': 'IDX'})
    df['Año'] = df['time'].str[:4].astype(int)
    df = df[df['Año'] >= 2015]
    return df.groupby('Año')['value'].mean().reset_index().rename(columns={'value': 'Valor'})

# === Sidebar ===
st.sidebar.title("🎯 Filtros")
rango = st.sidebar.slider("Selecciona rango de años", 2015, 2025, (2016, 2023))

# === Visualización ===

def mostrar_indicador(nombre, df):
    df_filtrado = df[(df['Año'] >= rango[0]) & (df['Año'] <= rango[1])]
    fig = px.line(df_filtrado, x='Año', y='Valor', markers=True, title=nombre)
    fig.update_layout(margin=dict(t=30, b=20), height=350)
    st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 PIB per cápita (€)")
    mostrar_indicador("PIB per cápita (CP_EUR_HAB)", obtener_pib())

with col2:
    st.subheader("📉 Tasa de paro (%)")
    mostrar_indicador("Tasa de paro (promedio anual)", obtener_paro())

st.subheader("🛒 Índice de Precios al Consumo (IPC)")
mostrar_indicador("IPC promedio anual (base 2015=100)", obtener_ipc())

st.markdown("---")
st.caption("📡 Fuente: Eurostat API — Datos siempre actualizados")
