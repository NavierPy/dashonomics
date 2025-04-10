from datetime import datetime
import pandas as pd
import requests
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashonomics", layout="wide")
st.title("📊 Dashonomics")
st.markdown("Indicadores económicos clave de España. Datos en tiempo real desde la API oficial de Eurostat.")

# ================================
# 🔧 Conversión de fechas
# ================================

def convertir_fecha_mensual(fecha_str):
    try:
        return datetime.strptime(fecha_str, "%YM%m")
    except ValueError:
        try:
            return datetime.strptime(fecha_str, "%Y-%m")
        except ValueError:
            return None

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
    params = {"geo": "ES", "unit": "CP_EUR_HAB", "na_item": "B1GQ", "format": "JSON"}
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
    params = {"geo": "ES", "coicop": "CP00", "unit": "I15", "format": "JSON"}
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
    params = {"geo": "ES", "sex": "T", "age": "TOTAL", "unit": "PC_ACT", "format": "JSON"}
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
# ⚠️ Índice de Riesgo Económico
# ================================

@st.cache_data
def calcular_indice_riesgo():
    df_pib = obtener_pib_trimestral()
    df_paro = obtener_paro_mensual()
    df_ipc = obtener_ipc_mensual()

    riesgo = 0
    motivos = []

    if len(df_pib) >= 2:
        pib_actual = df_pib.iloc[-1]["Valor"]
        pib_anterior = df_pib.iloc[-2]["Valor"]
        if pib_actual < pib_anterior:
            riesgo += 40
            motivos.append("📉 El PIB ha caído respecto al trimestre anterior.")

    if len(df_paro) >= 4:
        paro_actual = df_paro.iloc[-1]["Valor"]
        paro_pasado = df_paro.iloc[-4]["Valor"]
        if paro_actual > paro_pasado + 0.5:
            riesgo += 30
            motivos.append("📈 El desempleo ha subido significativamente en los últimos 3 meses.")

    if len(df_ipc) >= 2:
        ipc_actual = df_ipc.iloc[-1]["Valor"]
        ipc_anterior = df_ipc.iloc[-2]["Valor"]
        variacion = ipc_actual - ipc_anterior
        if abs(variacion) > 0.8:
            riesgo += 30
            if variacion > 0:
                motivos.append("🔥 La inflación mensual es muy elevada.")
            else:
                motivos.append("🧊 Riesgo de deflación: IPC ha caído bruscamente.")

    return min(riesgo, 100), motivos

# Generamos la nueva función `mostrar_reloj_riesgo_real` para Dashonomics con una aguja realista
def mostrar_reloj_riesgo_real(valor_riesgo):
    import plotly.graph_objects as go
    import numpy as np

    # Convertimos el valor a un ángulo (0 = izquierda, 100 = derecha)
    angulo = 180 * (1 - valor_riesgo / 100)
    angulo_rad = np.radians(angulo)
    x_final = 0.5 + 0.4 * np.cos(angulo_rad)
    y_final = 0.5 + 0.4 * np.sin(angulo_rad)

    fig = go.Figure()

    # Fondo del semicírculo: verde, naranja, rojo
    fig.add_trace(go.Pie(
        values=[30, 40, 30, 100],  # El último 100 es transparente
        rotation=180,
        hole=0.6,
        direction="clockwise",
        marker_colors=["green", "orange", "red", "rgba(0,0,0,0)"],
        text=["Bajo", "Medio", "Alto", ""],
        textinfo="label",
        hoverinfo="skip",
        showlegend=False
    ))

    # Aguja (línea negra)
    fig.add_shape(
        type="line",
        x0=0.5, y0=0.5,
        x1=x_final, y1=y_final,
        line=dict(color="black", width=4)
    )

    # Círculo central
    fig.add_shape(
        type="circle",
        x0=0.48, x1=0.52,
        y0=0.48, y1=0.52,
        fillcolor="black",
        line_color="black"
    )

    # Valor numérico
    fig.add_trace(go.Scatter(
        x=[0.5], y=[0.3],
        text=[f"{valor_riesgo}"],
        mode="text",
        textfont=dict(size=40, color="black"),
        hoverinfo="skip"
    ))

    fig.update_layout(
        margin=dict(t=30, b=30, l=30, r=30),
        showlegend=False,
        height=360,
        paper_bgcolor="white",
        xaxis=dict(showticklabels=False, range=[0, 1]),
        yaxis=dict(showticklabels=False, range=[0, 1])
    )

    st.plotly_chart(fig, use_container_width=True)





# ================================
# ⏰ Mostrar Reloj de Crisis
# ================================

st.header("⏰ Reloj de Crisis Económica")
indice, razones = calcular_indice_riesgo()
mostrar_reloj_riesgo(indice)

if razones:
    st.markdown("### ⚠️ Señales detectadas:")
    for r in razones:
        st.markdown(f"- {r}")
else:
    st.success("Todo en calma. No se detectan señales de alerta económica.")

# ================================
# 🎛️ Filtros dinámicos
# ================================

fechas_combinadas = pd.concat([
    obtener_pib_trimestral()["Fecha"],
    obtener_ipc_mensual()["Fecha"],
    obtener_paro_mensual()["Fecha"]
])
min_year = fechas_combinadas.dt.year.min()
max_year = fechas_combinadas.dt.year.max()

st.sidebar.title("🎯 Filtros")
rango = st.sidebar.slider("Rango de años", min_year, max_year, (max(max_year - 5, min_year), max_year))

# ================================
# 📊 Visualización de series
# ================================

def mostrar_serie(nombre, df):
    df_filtrado = df[df['Fecha'].dt.year.between(rango[0], rango[1])]
    fig = px.line(df_filtrado, x='Fecha', y='Valor', title=nombre)
    fig.update_layout(height=350, margin=dict(t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

st.subheader("🛒 IPC (mensual)")
mostrar_serie("Índice de Precios al Consumo (base 2015)", obtener_ipc_mensual())

col1, col2 = st.columns(2)

with col1:
    st.subheader("📉 Tasa de paro (mensual)")
    mostrar_serie("Paro (%)", obtener_paro_mensual())

with col2:
    st.subheader("📈 PIB per cápita (trimestral)")
    mostrar_serie("PIB per cápita [€]", obtener_pib_trimestral())

st.markdown("---")
st.caption("📡 Fuente: Eurostat REST API | Datos actualizados automáticamente")
