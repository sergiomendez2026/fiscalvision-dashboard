import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from pathlib import Path

st.set_page_config(
    page_title="FiscalVision AI Tax Analytics Platform",
    layout="wide"
)

DATA_PATH = Path("data/sri_ventas_2025.csv")
LOGO_PATH = Path("images/logo.png")

PROVINCE_COORDS = {
    "AZUAY": [-2.9006, -79.0045],
    "BOLIVAR": [-1.5931, -79.0000],
    "CAÑAR": [-2.5600, -78.9400],
    "CARCHI": [0.8119, -77.7173],
    "CHIMBORAZO": [-1.6635, -78.6546],
    "COTOPAXI": [-0.9333, -78.6167],
    "EL ORO": [-3.2581, -79.9554],
    "ESMERALDAS": [0.9682, -79.6517],
    "GALAPAGOS": [-0.9538, -90.9656],
    "GUAYAS": [-2.1709, -79.9224],
    "IMBABURA": [0.3517, -78.1223],
    "LOJA": [-3.9931, -79.2042],
    "LOS RIOS": [-1.8000, -79.5340],
    "MANABI": [-1.0546, -80.4525],
    "MORONA SANTIAGO": [-2.3087, -78.1114],
    "NAPO": [-0.9956, -77.8129],
    "ORELLANA": [-0.4629, -76.9872],
    "PASTAZA": [-1.4924, -78.0024],
    "PICHINCHA": [-0.1807, -78.4678],
    "SANTA ELENA": [-2.2267, -80.8587],
    "SANTO DOMINGO DE LOS TSACHILAS": [-0.2530, -79.1754],
    "SUCUMBIOS": [0.0889, -76.8898],
    "TUNGURAHUA": [-1.2491, -78.6167],
    "ZAMORA CHINCHIPE": [-4.0692, -78.9567],
}

CIIU_N1 = {
    "A": "Agricultura, ganadería, silvicultura y pesca",
    "B": "Explotación de minas y canteras",
    "C": "Industrias manufactureras",
    "D": "Suministro de electricidad, gas, vapor y aire acondicionado",
    "E": "Distribución de agua, alcantarillado y saneamiento",
    "F": "Construcción",
    "G": "Comercio al por mayor y menor; reparación de vehículos",
    "H": "Transporte y almacenamiento",
    "I": "Alojamiento y servicio de comidas",
    "J": "Información y comunicación",
    "K": "Actividades financieras y de seguros",
    "L": "Actividades inmobiliarias",
    "M": "Actividades profesionales, científicas y técnicas",
    "N": "Servicios administrativos y de apoyo",
    "O": "Administración pública y defensa",
    "P": "Enseñanza",
    "Q": "Salud humana y asistencia social",
    "R": "Artes, entretenimiento y recreación",
    "S": "Otras actividades de servicios",
    "T": "Actividades de los hogares",
    "U": "Organizaciones y órganos extraterritoriales",
}

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


def money_m(value):
    return f"${value / 1_000_000:,.2f} M"

def kpi_card(title, value, icon):
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #111827, #1f2937);
            padding: 22px;
            border-radius: 18px;
            border: 1px solid #374151;
            box-shadow: 0 4px 18px rgba(0,0,0,0.25);
            text-align: center;
            min-height: 130px;
        ">
            <div style="font-size: 28px;">{icon}</div>
            <div style="font-size: 14px; color: #9ca3af; margin-top: 8px;">{title}</div>
            <div style="font-size: 28px; font-weight: 700; color: white; margin-top: 8px;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_map(provincia_data):
    m = folium.Map(
        location=[-1.83, -78.18],
        zoom_start=6,
        tiles="CartoDB dark_matter"
    )

    max_sales = provincia_data["TOTAL_VENTAS"].max()

    for _, row in provincia_data.iterrows():
        provincia = row["PROVINCIA"]
        coords = PROVINCE_COORDS.get(provincia)

        if coords is None:
            continue

        radius = 8
        if max_sales > 0:
            radius = 8 + (row["TOTAL_VENTAS"] / max_sales) * 28

        popup = f"""
        <b>{provincia}</b><br>
        Ventas: {money_m(row["TOTAL_VENTAS"])}<br>
        Compras: {money_m(row["TOTAL_COMPRAS"])}
        """

        folium.CircleMarker(
            location=coords,
            radius=radius,
            popup=popup,
            tooltip=f"{provincia}: {money_m(row['TOTAL_VENTAS'])}",
            color="#38bdf8",
            fill=True,
            fill_color="#38bdf8",
            fill_opacity=0.65,
            weight=2,
        ).add_to(m)

    return m


df = load_data()

if LOGO_PATH.exists():
    st.sidebar.image(str(LOGO_PATH), width=180)

st.sidebar.title("FiscalVision AI")
st.sidebar.caption("Tax Analytics Platform")

menu = st.sidebar.radio(
    "Navegación",
    ["Executive Overview", "Geographic Analysis", "Data Explorer"]
)

st.sidebar.divider()
st.sidebar.header("Filtros")

provincia_opcion = st.sidebar.selectbox(
    "Provincia",
    options=["Todas"] + sorted(df["PROVINCIA"].dropna().unique().tolist())
)

mes_opcion = st.sidebar.selectbox(
    "Mes",
    options=["Todos"] + sorted(df["MES"].dropna().unique().tolist())
)

sectores_descripcion = {
    "A": "Agricultura, ganadería, silvicultura y pesca",
    "B": "Explotación de minas y canteras",
    "C": "Industrias manufactureras",
    "D": "Electricidad, gas y aire acondicionado",
    "E": "Agua, alcantarillado y saneamiento",
    "F": "Construcción",
    "G": "Comercio al por mayor y menor",
    "H": "Transporte y almacenamiento",
    "I": "Alojamiento y servicios de comida",
    "J": "Información y comunicación",
    "K": "Actividades financieras y seguros",
    "L": "Actividades inmobiliarias",
    "M": "Actividades profesionales, científicas y técnicas",
    "N": "Servicios administrativos y apoyo",
    "O": "Administración pública y defensa",
    "P": "Enseñanza",
    "Q": "Salud humana y asistencia social",
    "R": "Arte, entretenimiento y recreación",
    "S": "Otras actividades de servicios",
    "T": "Actividades de los hogares",
    "U": "Organizaciones extraterritoriales"
}

opciones_sector = ["Todas"] + list(sectores_descripcion.values())

sector_nombre = st.sidebar.selectbox(
    "Actividad económica",
    opciones_sector
)

df_filtrado = df.copy()

if provincia_opcion != "Todas":
    df_filtrado = df_filtrado[df_filtrado["PROVINCIA"] == provincia_opcion]

if mes_opcion != "Todos":
    df_filtrado = df_filtrado[df_filtrado["MES"] == mes_opcion]

codigo_sector = None

for codigo, descripcion in sectores_descripcion.items():
    if descripcion == sector_nombre:
        codigo_sector = codigo
        break

if codigo_sector:
    df_filtrado = df_filtrado[
        df_filtrado["CODIGO_SECTOR_N1"] == codigo_sector
    ]

if codigo_sector:
    descripcion_sector = sectores_descripcion.get(codigo_sector, "Sector no identificado")
    st.sidebar.info(f"{codigo_sector}: {descripcion_sector}")

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

canton_lider = (
    df_filtrado.groupby("CANTON")["TOTAL_VENTAS"]
    .sum()
    .sort_values(ascending=False)
    .index[0]
    if not df_filtrado.empty else "N/A"
)

margen = (diferencia / total_ventas * 100) if total_ventas > 0 else 0

st.markdown(
    """
    <h1 style="font-size:44px;">FiscalVision AI Dashboard</h1>
    <p style="font-size:17px; color:#9ca3af;">
    Executive tax analytics dashboard based on official SRI Ecuador 2025 sales and purchases data.
    </p>
    """,
    unsafe_allow_html=True,
)

if menu == "Executive Overview":
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        kpi_card("Total Ventas", money_m(total_ventas), "💰")
    with c2:
        kpi_card("Total Compras", money_m(total_compras), "🧾")
    with c3:
        kpi_card("Diferencia", money_m(diferencia), "📈")
    with c4:
        kpi_card("Registros", f"{registros:,}", "📄")
    with c5:
        kpi_card("Provincia Líder", provincia_lider, "🏆")

    st.divider()

    provincia_data = (
        df_filtrado.groupby("PROVINCIA", as_index=False)[["TOTAL_VENTAS", "TOTAL_COMPRAS"]]
        .sum()
        .sort_values("TOTAL_VENTAS", ascending=False)
    )

    col_map, col_gauge = st.columns([2, 1])

    with col_map:
        st.subheader("Mapa económico por provincia")
        st_folium(build_map(provincia_data), width=850, height=470)

    with col_gauge:
        st.subheader("Margen ventas-compras")
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=round(margen, 2),
                number={"suffix": "%"},
                title={"text": "Margen"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#38bdf8"},
                    "steps": [
                        {"range": [0, 25], "color": "#7f1d1d"},
                        {"range": [25, 60], "color": "#78350f"},
                        {"range": [60, 100], "color": "#064e3b"},
                    ],
                },
            )
        )
        fig_gauge.update_layout(height=340)
        st.plotly_chart(fig_gauge, use_container_width=True)

        st.info(
            f"📌 Insight: **{provincia_lider}** lidera las ventas declaradas. "
            f"El cantón con mayor volumen es **{canton_lider}**."
        )

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

    ventas_provincia = provincia_data.head(10)

    fig_bar = px.bar(
        ventas_provincia,
        x="TOTAL_VENTAS",
        y="PROVINCIA",
        orientation="h",
        title="Top 10 Provincias por Ventas",
        text_auto=".2s"
    )
    fig_bar.update_layout(yaxis={"categoryorder": "total ascending"})
    col6.plotly_chart(fig_bar, use_container_width=True)

    compras_provincia = (
        provincia_data
        .sort_values("TOTAL_COMPRAS", ascending=False)
        .head(10)
    )

    fig_bar2 = px.bar(
        compras_provincia,
        x="TOTAL_COMPRAS",
        y="PROVINCIA",
        orientation="h",
        title="Top 10 Provincias por Compras",
        text_auto=".2s"
    )
    fig_bar2.update_layout(yaxis={"categoryorder": "total ascending"})
    col7.plotly_chart(fig_bar2, use_container_width=True)

elif menu == "Geographic Analysis":
    st.subheader("Análisis geográfico")
    provincia_data = (
        df_filtrado.groupby("PROVINCIA", as_index=False)[["TOTAL_VENTAS", "TOTAL_COMPRAS"]]
        .sum()
        .sort_values("TOTAL_VENTAS", ascending=False)
    )
    st_folium(build_map(provincia_data), width=1200, height=620)
    provincia_data_display = provincia_data.copy()

    provincia_data_display["TOTAL_VENTAS"] = provincia_data_display["TOTAL_VENTAS"].apply(money_m)
    provincia_data_display["TOTAL_COMPRAS"] = provincia_data_display["TOTAL_COMPRAS"].apply(money_m)

    st.dataframe(provincia_data_display, use_container_width=True)

elif menu == "Data Explorer":
    st.subheader("Vista de datos")
    st.download_button(
        "Descargar datos filtrados CSV",
        df_filtrado.to_csv(index=False).encode("utf-8-sig"),
        "fiscalvision_filtered_data.csv",
        "text/csv"
    )

df_display = df_filtrado.head(500).copy()

columnas_monetarias = [
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

for col in columnas_monetarias:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(money_m)

st.dataframe(df_display, use_container_width=True)
