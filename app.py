import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="FiscalVision AI Tax Analytics Platform",
    layout="wide"
)

DATA_PATH = Path("data/sri_ventas_2025.csv")
LOGO_PATH = Path("images/logo.png")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")

    numeric_cols = [
        "VENTAS_NETAS_TARIFA_GRAVADA",
        "VENTAS_NETAS_TARIFA_0",
        "VENTAS_NETAS_TARIFA_VARIABLE",
        "VENTAS_NETAS_TARIFA_5",
        "EXPORTACIONES",
        "COMPRAS_NETAS_TARIFA_GRAVADA",
        "COMPRAS_NETAS_TARIFA_0",
        "IMPORTACIONES",
        "COMPRAS_RISE",
        "TOTAL_VENTAS",
        "TOTAL_COMPRAS",
    ]

    for col in numeric_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


df = load_data()

header_col1, header_col2 = st.columns([1, 5])

with header_col1:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=120)

with header_col2:
    st.title("FiscalVision AI Dashboard")
    st.caption("Tax analytics platform based on official SRI Ecuador 2025 sales and purchases dataset.")

st.sidebar.header("Filtros")

provincias = st.sidebar.multiselect(
    "Provincia",
    options=sorted(df["PROVINCIA"].dropna().unique()),
    default=sorted(df["PROVINCIA"].dropna().unique())
)

meses = st.sidebar.multiselect(
    "Mes",
    options=sorted(df["MES"].dropna().unique()),
    default=sorted(df["MES"].dropna().unique())
)

df_filtrado = df[
    (df["PROVINCIA"].isin(provincias)) &
    (df["MES"].isin(meses))
]

total_ventas = df_filtrado["TOTAL_VENTAS"].sum()
total_compras = df_filtrado["TOTAL_COMPRAS"].sum()
diferencia = total_ventas - total_compras
registros = len(df_filtrado)

provincia_lider = (
    df_filtrado.groupby("PROVINCIA")["TOTAL_VENTAS"]
    .sum()
    .sort_values(ascending=False)
    .index[0]
    if not df_filtrado.empty else "N/A"
)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total ventas", f"${total_ventas/1_000_000:,.1f} M")
col2.metric("Total compras", f"${total_compras/1_000_000:,.1f} M")
col3.metric("Diferencia", f"${diferencia/1_000_000:,.1f} M")
col4.metric("Registros", f"{registros:,}")
col5.metric("Provincia líder", provincia_lider)

st.divider()

ventas_mes = df_filtrado.groupby("MES", as_index=False)[["TOTAL_VENTAS", "TOTAL_COMPRAS"]].sum()

fig_line = px.line(
    ventas_mes,
    x="MES",
    y=["TOTAL_VENTAS", "TOTAL_COMPRAS"],
    markers=True,
    title="Ventas vs Compras por Mes"
)

st.plotly_chart(fig_line, use_container_width=True)

col6, col7 = st.columns(2)

ventas_provincia = (
    df_filtrado.groupby("PROVINCIA", as_index=False)["TOTAL_VENTAS"]
    .sum()
    .sort_values("TOTAL_VENTAS", ascending=False)
    .head(10)
)

fig_bar = px.bar(
    ventas_provincia,
    x="PROVINCIA",
    y="TOTAL_VENTAS",
    title="Top 10 Provincias por Ventas"
)

col6.plotly_chart(fig_bar, use_container_width=True)

compras_provincia = (
    df_filtrado.groupby("PROVINCIA", as_index=False)["TOTAL_COMPRAS"]
    .sum()
    .sort_values("TOTAL_COMPRAS", ascending=False)
    .head(10)
)

fig_bar2 = px.bar(
    compras_provincia,
    x="PROVINCIA",
    y="TOTAL_COMPRAS",
    title="Top 10 Provincias por Compras"
)

col7.plotly_chart(fig_bar2, use_container_width=True)

st.subheader("Vista de datos")
st.dataframe(df_filtrado.head(100), use_container_width=True)