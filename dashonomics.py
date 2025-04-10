import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashonomics", layout="wide")
st.title("📊 Dashonomics")
st.markdown("Explora la evolución de indicadores económicos clave de España. Datos en tiempo real desde Eurostat (CSV actualizado automáticamente).")

# === URLs oficiales de Eurostat con datos actualizados ===

URL_PIB = "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/nama_10_pc.tsv.gz"
URL_PARO = "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/une_rt_m.tsv.gz"
URL_IPC = "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/prc_hicp_midx.tsv.gz"

# === Funciones para cargar y filtrar datos ===

@st.cache_data
def cargar_pib():
    df = pd.read_csv(URL_PIB, compression='gzip', sep='\t')
    df = df[df['unit,geo'] == 'CP_EUR_HAB,ES']
    df = df.drop(columns=['unit,geo']).T.reset_index()
    df.columns = ['Año', 'Valor']
    df['Año'] = df['Año'].str.extract(r'(\d{4})').astype(int)
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
    return df.dropna()

@st.cache_data
def cargar_paro():
    df = pd.read_csv(URL_PARO, compression='gzip', sep='\t')
    df = df[df['unit,sex,age,geo'] == 'PC_ACT,TOTAL,Y15-74,ES']
    df = df.drop(columns=['unit,sex,age,geo']).T.reset_index()
    df.columns = ['Fecha', 'Valor']
    df['Año'] = df['Fecha'].str.extract(r'(\d{4})').astype(int)
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
    return df.groupby('Año')['Valor'].mean().reset_index()

@st.cache_data
def cargar_ipc():
    df = pd.read_csv(URL_IPC, compression='gzip', sep='\t')
    df = df[df['coicop,unit,geo,indic'] == 'CP00,INX,ES,IDX']
    df = df.drop(columns=['coicop,unit,geo,indic']).T.reset_index()
    df.columns = ['Fecha', 'Valor']
    df['Año'] = df['Fecha'].str.extract(r'(\d{4})').astype(int)
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
    return df.groupby('Año')['Valor'].mean().reset_index()

# === Sidebar ===
st.sidebar.title("🎯 Filtros")
rango = st.sidebar.slider("Selecciona rango de años", 2000, 2025, (2015, 2023))

# === Visualización ===

def mostrar_indicador(nombre, df):
    df_filtrado = df[(df['Año'] >= rango[0]) & (df['Año'] <= rango[1])]
    fig = px.line(df_filtrado, x='Año', y='Valor', markers=True, title=nombre)
    fig.update_layout(margin=dict(t=30, b=20), height=350)
    st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 PIB per cápita (€)")
    mostrar_indicador("PIB per cápita (CP_EUR_HAB)", cargar_pib())

with col2:
    st.subheader("📉 Tasa de paro (%)")
    mostrar_indicador("Tasa de paro (promedio anual)", cargar_paro())

st.subheader("🛒 Índice de Precios al Consumo (IPC)")
mostrar_indicador("IPC base 2015 = 100 (promedio anual)", cargar_ipc())

st.markdown("---")
st.caption("📡 Fuente: Eurostat (datos descargados automáticamente en cada carga)")
