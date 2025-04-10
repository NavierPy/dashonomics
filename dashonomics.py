import streamlit as st
import pandas as pd
import plotly.express as px
from pandasdmx import Request

st.set_page_config(page_title="Dashonomics", layout="wide")
st.title("📊 Dashonomics")
st.markdown("Explora la evolución de los indicadores clave de la economía española con datos en tiempo real de Eurostat.")

# === Funciones de carga de datos ===

@st.cache_data
def obtener_pib(pais='ES'):
    estat = Request('EUROSTAT')
    data_response = estat.data(resource_id='nama_10_pc', key=f'{pais}.B1GQ.CP_EUR_HAB.A', params={'startPeriod': '2015'})
    data = data_response.to_pandas()
    pib = data['Value'].reset_index()
    pib.columns = ['Año', 'Valor']
    pib['Año'] = pib['Año'].astype(int)
    return pib

@st.cache_data
def obtener_ipc(pais='ES'):
    estat = Request('EUROSTAT')
    data_response = estat.data(resource_id='prc_hicp_midx', key=f'{pais}.CP00.I10.2015_M.INDX', params={'startPeriod': '2015'})
    data = data_response.to_pandas()
    ipc = data['Value'].reset_index()
    ipc['Año'] = ipc['TIME_PERIOD'].dt.year
    ipc = ipc.groupby('Año')['Value'].mean().reset_index()
    ipc.columns = ['Año', 'Valor']
    return ipc

@st.cache_data
def obtener_paro(pais='ES'):
    estat = Request('EUROSTAT')
    data_response = estat.data(resource_id='une_rt_m', key=f'{pais}.M.TOTAL.UNE_RT_M.A', params={'startPeriod': '2015'})
    data = data_response.to_pandas()
    paro = data['Value'].reset_index()
    paro['Año'] = paro['TIME_PERIOD'].dt.year
    paro = paro.groupby('Año')['Value'].mean().reset_index()
    paro.columns = ['Año', 'Valor']
    return paro

# === Sidebar ===

st.sidebar.title("🎯 Filtros")
rango_anos = st.sidebar.slider("Selecciona rango de años", 2015, 2025, (2016, 2023))

# === Visualización de indicadores ===

def mostrar_indicador(nombre, df):
    df_filtrado = df[(df['Año'] >= rango_anos[0]) & (df['Año'] <= rango_anos[1])]
    fig = px.line(df_filtrado, x='Año', y='Valor', markers=True, title=nombre)
    fig.update_layout(margin=dict(t=30, b=20), height=350)
    st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 PIB per cápita (€)")
    df_pib = obtener_pib()
    mostrar_indicador("PIB per cápita (miles de euros)", df_pib)

with col2:
    st.subheader("📉 Tasa de paro (%)")
    df_paro = obtener_paro()
    mostrar_indicador("Tasa de paro", df_paro)

with st.container():
    st.subheader("🛒 Índice de Precios al Consumo (IPC)")
    df_ipc = obtener_ipc()
    mostrar_indicador("IPC promedio anual (base 2015=100)", df_ipc)

st.markdown("---")
st.caption("📡 Fuente de datos: Eurostat • Actualización automática vía API")
