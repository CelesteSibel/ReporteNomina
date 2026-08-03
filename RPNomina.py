import streamlit as st
import pandas as pd
import plotly.express as px


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

st.image(
    "https://www.interbox.com.ec/wp-content/uploads/2020/01/logo_banco_internacional.png",
    width=580
)

st.set_page_config(
    page_title="Reporte Cartera Nómina",
    layout="wide"
)


st.markdown(
"""
<style>

[data-testid="stMetricValue"] {
    font-size: 22px;
}

[data-testid="stMetricLabel"] {
    font-size: 13px;
}

</style>
""",
unsafe_allow_html=True
)


st.title(
    "📊 Reporte Cartera Nómina" 
)



# ==========================================================
# DATA
# ==========================================================

df = pd.read_pickle(
    "DF_F1.pkl"
)



# ==========================================================
# FUNCIONES LIMPIEZA OPERACIONES
# ==========================================================


def limpiar_operaciones(ops):

    if not isinstance(ops, list) or len(ops) == 0:

        return pd.Series({

            "NumOperaciones":0,
            "EntidadesCredito":"",
            "SaldoVencidoOperaciones":0,
            "MaxDiasMoraSistema":0,
            "EntidadMayorMora":""

        })


    entidades = []
    saldo_vencido = 0
    max_mora = 0
    entidad_mora = ""


    for op in ops:

        entidad = op.get(
            "RazonSocial",
            ""
        )


        entidades.append(
            entidad
        )


        saldo_vencido += float(
            op.get(
                "ValorVencidoTotal",
                0
            )
        )


        mora = int(
            op.get(
                "DiasMorosidad",
                0
            )
        )


        if mora > max_mora:

            max_mora = mora
            entidad_mora = entidad



    return pd.Series({

        "NumOperaciones":len(ops),

        "EntidadesCredito":
            ", ".join(entidades),

        "SaldoVencidoOperaciones":
            saldo_vencido,

        "MaxDiasMoraSistema":
            max_mora,

        "EntidadMayorMora":
            entidad_mora

    })





# ==========================================================
# FUNCIONES LIMPIEZA TARJETAS
# ==========================================================


def limpiar_tarjetas(tarjetas):


    if not isinstance(tarjetas, list) or len(tarjetas)==0:

        return pd.Series({

            "NumTarjetas":0,
            "EntidadesTarjetas":"",
            "SaldoTarjetas":0,
            "CupoTarjetas":0,
            "SaldoVencidoTarjetas":0

        })


    entidades=[]
    saldo=0
    cupo=0
    saldo_vencido=0


    for tarjeta in tarjetas:


        entidad = (

            tarjeta.get(
                "Entidad"
            )

            or

            tarjeta.get(
                "RazonSocial"
            )

            or ""

        )


        entidades.append(
            entidad
        )


        saldo += float(
            tarjeta.get(
                "Saldo",
                0
            )
        )


        cupo += float(
            tarjeta.get(
                "Cupo",
                0
            )
        )


        saldo_vencido += float(
            tarjeta.get(
                "SaldoVencido",
                0
            )
        )



    return pd.Series({

        "NumTarjetas":len(tarjetas),

        "EntidadesTarjetas":
            ", ".join(entidades),

        "SaldoTarjetas":
            saldo,

        "CupoTarjetas":
            cupo,

        "SaldoVencidoTarjetas":
            saldo_vencido

    })



# ==========================================================
# PREPARACIÓN DE CAMPOS
# ==========================================================


df["DiasVencido"] = pd.to_numeric(
    df["DiasVencido"],
    errors="coerce"
).fillna(0)



df["SaldoActualBI"] = (
    pd.to_numeric(df["SaldoTotal_x"], errors="coerce").fillna(0)
    - pd.to_numeric(df["Interes"], errors="coerce").fillna(0)
    - pd.to_numeric(df["InteresMora"], errors="coerce").fillna(0)
)



df["SaldoActualSF"] = pd.to_numeric(
    df["SaldoTotal_y"],
    errors="coerce"
).fillna(0)

# ==========================================================
# VARIABLES CALCULADAS
# ==========================================================




# ==========================================================
# LIMPIAR OPERACIONES Y TARJETAS
# ==========================================================


if "OperacionesVigentes" in df.columns:


    df[
        [
            "NumOperaciones",
            "EntidadesCredito",
            "SaldoVencidoOperaciones",
            "MaxDiasMoraSistema",
            "EntidadMayorMora"

        ]
    ] = df[
        "OperacionesVigentes"
    ].apply(
        limpiar_operaciones
    )



if "DetalleTarjetas" in df.columns:


    df[
        [
            "NumTarjetas",
            "EntidadesTarjetas",
            "SaldoTarjetas",
            "CupoTarjetas",
            "SaldoVencidoTarjetas"

        ]
    ] = df[
        "DetalleTarjetas"
    ].apply(
        limpiar_tarjetas
    )



# ==========================================================
# SALDO VENCIDO SF
# ==========================================================


df["SaldoVencidoSF"] = (

    df["SaldoVencidoOperaciones"].fillna(0)

    +

    df["SaldoVencidoTarjetas"].fillna(0)

)



# ==========================================================
# FILTROS
# ==========================================================


st.sidebar.header(
    "🔎 Filtros"
)



cliente = st.sidebar.text_input(
    "Buscar cliente"
)



id_cliente = st.sidebar.text_input(
    "Buscar Id"
)



rango_mora = st.sidebar.slider(

    "Días vencidos",

    int(df["DiasVencido"].min()),

    int(df["DiasVencido"].max()),

    (

        int(df["DiasVencido"].min()),

        int(df["DiasVencido"].max())

    )

)



# Copia para filtros

data = df.copy()



# Buscar cliente

if cliente:


    data = data[

        data["Nombre"]

        .astype(str)

        .str.contains(

            cliente,

            case=False,

            na=False

        )

    ]



# Buscar Id

if id_cliente:


    data = data[

        data["Id"]

        .astype(str)

        .str.contains(

            id_cliente,

            case=False,

            na=False

        )

    ]



# Rango días vencidos

data = data[

    (data["DiasVencido"] >= rango_mora[0])

    &

    (data["DiasVencido"] <= rango_mora[1])

]





# ==========================================================
# INDICADORES PRINCIPALES
# ==========================================================


st.subheader(
    "📌 Indicadores principales"
)



c1,c2,c3,c4,c5,c6 = st.columns(6)



c1.metric(

    "Clientes",

    data["CodigoCliente"].nunique()

)



c2.metric(

    "Monto Aprobado",

    f"${data['MontoAprobado_y'].sum():,.0f}"

)




c4.metric(

    "SaldoActualBI",

    f"${data['SaldoActualBI'].sum():,.0f}"

)



c5.metric(

    "SaldoActualSF",

    f"${data['SaldoActualSF'].sum():,.0f}"

)



c6.metric(

    "SaldoVencidoSF",

    f"${data['SaldoVencidoSF'].sum():,.0f}"

)




# ==========================================================
# DETALLE CLIENTES
# ==========================================================



st.subheader(
    "👤 Detalle Clientes"
)



columnas = [

    "Id",

    "Nombre",


    "DiasVencido",


    "Score",

    "ScoreF",

    "SaldoActualBI",

    "SaldoActualSF",


    "SaldoVencidoSF",


    "SaldoVencidoOperaciones",

    "SaldoVencidoTarjetas",


    "MaxDiasMoraSistema",

    "EntidadMayorMora",


    "NumOperaciones",

    "EntidadesCredito",


    "NumTarjetas",

    "EntidadesTarjetas","Estado","Lugar" ,"UltimaFechaAfiliacion"

]



columnas = [

    x for x in columnas

    if x in data.columns

]



st.dataframe(

    data[columnas],

    use_container_width=True,

    height=600

)



# ==========================================================
# GRÁFICO CLIENTE: SALDO ACTUAL BI Y DÍAS VENCIDOS
# ==========================================================


st.subheader(
    "📊 Clientes: SaldoActualBI y Días Vencidos"
)


grafico_cliente = (

    data[

        [
            "Nombre",
            "DiasVencido",
            "SaldoActualBI"

        ]

    ]

    .groupby(
        "Nombre"
    )

    .agg(

        DiasVencido=(
            "DiasVencido",
            "max"
        ),

        SaldoActualBI=(
            "SaldoActualBI",
            "sum"
        )

    )

    .reset_index()

)



fig = px.bar(

    grafico_cliente,

    x="Nombre",

    y="SaldoActualBI",

    color="SaldoActualBI",

    text_auto=True

)



fig.add_scatter(

    x=grafico_cliente["Nombre"],

    y=grafico_cliente["DiasVencido"],

    mode="lines+markers",

    name="Días Vencidos",

    yaxis="y2"

)



fig.update_layout(

    xaxis_title="Cliente",

    yaxis_title="SaldoActualBI",

    yaxis2=dict(

        title="Días Vencidos",

        overlaying="y",

        side="right"

    ),

    xaxis=dict(

        tickangle=-45

    ),

    hovermode="x unified"

)



st.plotly_chart(

    fig,

    use_container_width=True

)

# ==========================================================
# GRÁFICO DE LÍNEAS POR CLIENTE
# DÍAS VENCIDOS VS SALDO TOTAL
# ==========================================================


st.subheader(
    "📈 Evolución SaldoTotal por Cliente según Días Vencidos"
)


grafico_cliente = (

    data[

        [
            "Nombre",
            "DiasVencido",
            "SaldoActualBI"

        ]

    ]

    .sort_values(
        "DiasVencido"
    )

)



fig = px.line(

    grafico_cliente,

    x="DiasVencido",

    y="SaldoActualBI",

    color="Nombre",

    markers=True,

    hover_name="Nombre",

    hover_data={

        "DiasVencido": True,

        "SaldoActualBI": ":,.0f"

    }

)



fig.update_layout(

    xaxis_title="Días vencidos",

    yaxis_title="SaldoActualBI",

    legend_title="Cliente",

    hovermode="x unified"

)



st.plotly_chart(

    fig,

    use_container_width=True

)