# 📦 Importar librerías
import os
import json
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import unicodedata


# 🔐 Usuarios y roles (asegurando coincidencia exacta con df['VENDEDOR'])
USUARIOS = {
    "admin": {"password": "admin", "vendedor": "ALL"},
    "Guillermo": {"password": "47835765", "vendedor": "GUILLERMO"},
    "JorgeChavez": {"password": "5678", "vendedor": "JORGE CHAVEZ"},  # corregido
    "JoseCarlos": {"password": "77298007", "vendedor": "JOSE CARLOS"},
    "MariaJanet": {"password": "76029937", "vendedor": "MARIA JANET"},
    "Milena": {"password": "9999", "vendedor": "MILENA"},
    "WalterBejarano": {"password": "9999", "vendedor": "WALTER BEJARANO"},
    "YeseniaFlores": {"password": "9999", "vendedor": "YESENIA FLORES"},
    # agrega más vendedores según tu Excel
}

st.markdown(
    """
    # 🌟 Bienvenido al Dashboard de Ventas 🌟
    ---
    Este aplicativo ha sido creado con el objetivo de informar las ventas desde el año 2023 hasta la fecha.

    Saludos...!.

    ---
    """
)


# 🧭 Estado de sesión
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "vendedor_actual" not in st.session_state:
    st.session_state.vendedor_actual = None

# 🚪 Logout
def logout():
    st.session_state.usuario = None
    st.session_state.vendedor_actual = None

# 🎨 Configurar estilo visual
st.set_page_config(page_title="Dashboard de Ventas - KBA ELECTRIC", layout="wide", page_icon="📊")

# 🔑 Login de vendedores
if st.session_state.usuario is None:
    col_login = st.columns([2, 3, 2])[1]
    with col_login:
        st.markdown("### 🔑 Ingreso al Dashboard de ventas")
        usuario_input = st.text_input("Usuario", placeholder="ej. admin, Guillermo, JorgeChavez, JoseCarlos, MariaJanet, Milena, WalterBejarano, YeseniaFlores")
        password_input = st.text_input("Contraseña", type="password", placeholder="Tu contraseña")
        if st.button("Ingresar"):
            
            if usuario_input in USUARIOS and USUARIOS[usuario_input]["password"] == password_input:
                st.session_state.usuario = usuario_input
                st.session_state.vendedor_actual = USUARIOS[usuario_input]["vendedor"]
                st.success(f"Bienvenido, {usuario_input}.")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

    st.markdown("<p style='text-align:center; color:gray; font-size:14px;'>Aplicativo desarrollado por <b>Edward O.</b> © 2025</p>", unsafe_allow_html=True)
    st.stop()  # Detiene la app hasta que haya login
    

# 🧠 Cargar datos automáticamente al iniciar
if "df" not in st.session_state:
    try:
        df = pd.read_excel("ventas.xlsm", sheet_name='Ventas', header=0)
        st.session_state["df"] = df
        st.success("✅ Datos cargados automáticamente desde ventas.xlsm")
    except Exception as e:
        st.error(f"❌ No se pudo cargar el archivo Excel: {e}")

# 🔄 Botón para recargar datos manualmente
if st.button("🔄 Recargar datos desde Excel"):
    try:
        df = pd.read_excel("ventas.xlsm", sheet_name='Ventas', header=0)
        st.session_state["df"] = df
        st.success("✅ Datos recargados correctamente.")
    except Exception as e:
        st.error(f"❌ Error al recargar datos: {e}")

# ✅ Verificar si los datos están cargados
if "df" in st.session_state:
    df = st.session_state["df"]

    # 🧼 Limpieza de columnas
    df.columns = [str(c).replace('/', '').strip().upper() for c in df.columns]

    # 🔢 Convertir columnas clave
    df['TOTAL'] = pd.to_numeric(df['TOTAL'], errors='coerce')
    df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')

    # 🧠 Derivar columna AÑO y MES desde FECHA si no existen o están vacías
    if 'AÑO' not in df.columns or df['AÑO'].isnull().all():
        df['AÑO'] = df['FECHA'].dt.year
    if 'MES' not in df.columns or df['MES'].isnull().all():
        df['MES'] = df['FECHA'].dt.strftime('%b').str.capitalize()

    # 🧹 Normalización de texto
    df['VENDEDOR'] = df['VENDEDOR'].astype(str).str.strip().str.upper()
    df['EMPRESA'] = df['EMPRESA'].astype(str).str.strip().str.upper()
    df['MES'] = df['MES'].astype(str).str.strip().str.capitalize()

    # 🔒 Normalización de nombres de empresa
    df['EMPRESA'] = df['EMPRESA'].replace({
        'TEAMWORK': 'TEAMWORK KBA',
        'TEAMWORK KBA': 'TEAMWORK KBA',
        'INDUSTRIAS ELECTRICAS': 'INDUSTRIAS ELECTRICAS KBA',
        'INDUSTRIAS ELECTRICAS R&A S.A.C.': 'INDUSTRIAS ELECTRICAS KBA',
        'INDUSTRIAS ELECTRICAS KBA SAC': 'INDUSTRIAS ELECTRICAS KBA'
    })

    # 🧹 Correcciones manuales de vendedores (incluye variantes de José Carlos)
    correcciones = {
        "CARLOS AMADO": "AMADO",
        "JUAN BALBAZO": "BALBAZO",
        "VICTOR BALBAZO": "BALBAZO",
        "JORGE RAMIREZ GARCIA": "JORGE RAMIREZ",
        "JOSE CARLOS RAMIREZ": "JOSE CARLOS",
        "JOSÉ CARLOS": "JOSE CARLOS",
        "JOSE CARLOS ": "JOSE CARLOS"
    }
    df['VENDEDOR'] = df['VENDEDOR'].replace(correcciones)

    # 👤 Contexto de usuario
    usuario = st.session_state.usuario
    vendedor_actual = st.session_state.vendedor_actual

    st.sidebar.markdown(f"**👤 Usuario:** {usuario}")
    st.sidebar.button("Cerrar sesión", on_click=logout)

    # 🔒 Filtro automático por vendedor (aplicar DESPUÉS de limpiar y corregir)
    if vendedor_actual != "ALL":
        df = df[df['VENDEDOR'] == vendedor_actual]
        st.info(f"🔒 Vista filtrada por vendedor: {vendedor_actual}")
    else:
        st.success("🛡️ Vista de administrador (todos los vendedores).")

    # 🖼️ Portada corporativa con logos
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        st.image("static/logo_kba.png", width=300)
    with col2:
        st.markdown("""
            <div style='background-color:#003366;padding:20px;border-radius:20px;text-align:center'>
                <h1 style='color:white;margin-bottom:5px;'>DASHBOARD DE VENTAS</h1>
                <h2 style='color:white;margin-top:0;'>INDUSTRIAS ELÉCTRICAS KBA SAC – TEAMWORK KBA</h2>
                <h3 style='color:white;margin-top:0;'>2023 – 2025</h3>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.image("static/logo_teamwork.png", width=250)

        # ✅ Línea de autoría fuera de la caja azul, centrada
st.markdown(
    "<div style='text-align:center; margin-top:-10px; margin-bottom:30px;'>"
    "<span style='color:#666; font-size:15px;'>Aplicativo desarrollado por <b>Edward O.</b> © 2025</span>"
    "</div>",
    unsafe_allow_html=True
)

    # 🎛️ Filtros visuales con activadores
with st.container():
    st.markdown("### 🎛️ Filtros dinámicos")

    col1, col2, col3, col4 = st.columns([3, 3, 3, 3])  # columnas más anchas

    with col1:
        activar_filtro_mes = st.checkbox("📅 Filtrar por mes", value=False)  # inicia desactivado
        if activar_filtro_mes:
            mes = st.selectbox(
                label="Mes",
                options=['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                placeholder="Selecciona mes",
                label_visibility="visible"
            )
        else:
            mes = None

    with col2:
        activar_filtro_año = st.checkbox("📆 Filtrar por año", value=False)  # inicia desactivado
        if activar_filtro_año:
            año = st.selectbox(
                label="Año",
                options=[2023, 2024, 2025],
                format_func=lambda x: f"Año {x}",
                placeholder="Selecciona año",
                label_visibility="visible"
            )
        else:
            año = None

    with col3:
        activar_filtro_empresa = st.checkbox("🏢 Filtrar por empresa", value=False)  # inicia desactivado
        if activar_filtro_empresa:
            empresa = st.selectbox(
                label="Empresa",
                options=['INDUSTRIAS ELECTRICAS KBA', 'TEAMWORK KBA'],
                placeholder="Selecciona empresa",
                label_visibility="visible"
            )
        else:
            empresa = None

    with col4:
        activar_filtro_vendedor = st.checkbox("🧑‍💼 Filtrar por vendedor", value=False)  # inicia desactivado
        if activar_filtro_vendedor:
            vendedores = st.multiselect(
                label="Vendedor(es)",
                options=sorted(df['VENDEDOR'].unique()),
                default=[],
                placeholder="Selecciona vendedor(es)",
                label_visibility="visible"
            )
        else:
            vendedores = None

    # 🔍 Aplicar filtros dinámicos
    df_filtrado = df.copy()

    if activar_filtro_mes and mes:
        df_filtrado = df_filtrado[df_filtrado['MES'] == mes]

    if activar_filtro_año and año:
        df_filtrado = df_filtrado[df_filtrado['AÑO'] == año]

    if activar_filtro_empresa and empresa:
        df_filtrado = df_filtrado[df_filtrado['EMPRESA'] == empresa]

    if activar_filtro_vendedor and vendedores:
        df_filtrado = df_filtrado[df_filtrado['VENDEDOR'].isin(vendedores)]

    # 🔎 Validación visual
    st.write(f"🔎 Filas encontradas con el filtro actual: {len(df_filtrado)}")

    # 🧱 Base segura para gráficos: si no hay datos filtrados, usar el dataset completo
    df_base = df_filtrado if len(df_filtrado) > 0 else df

    # 📋 Ventas Totales por Año – Comparativo Elegante
    st.markdown("## 📋 Ventas Totales por Año – Comparativo Elegante")
    ventas_tabla = df_base[df_base['AÑO'].isin([2023, 2024, 2025])] \
        .groupby(['EMPRESA', 'AÑO'])['TOTAL'].sum().reset_index()

    if not ventas_tabla.empty:
        tabla_pivot = ventas_tabla.pivot(index='AÑO', columns='EMPRESA', values='TOTAL').fillna(0)
        tabla_pivot = tabla_pivot.rename(columns={
            'INDUSTRIAS ELECTRICAS KBA': 'INDUSTRIAS ELECTRICAS K&A',
            'TEAMWORK KBA': 'TEAMWORK K&A'
        })
        tabla_formateada = tabla_pivot.applymap(lambda x: f"S/ {x:,.2f}")
        st.dataframe(
            tabla_formateada.style.set_properties(**{
                'background-color': '#ffffff',
                'color': '#000000',
                'border': '1px solid #cccccc',
                'font-size': '16px',
                'text-align': 'center',
                'font-family': 'Segoe UI'
            }).set_caption("💼 Comparativo de Ventas Totales por Año (2023–2025)")
        )
    else:
        st.info("ℹ️ No hay datos para el comparativo con el contexto actual.")

    # 📈 Comportamiento de las Ventas 2023–2025
    st.markdown("## 📈 Comportamiento de las Ventas 2023–2025")
    ventas_crecimiento = df_base[df_base['AÑO'].isin([2023, 2024, 2025])] \
        .groupby('AÑO')['TOTAL'].sum().reset_index().sort_values('AÑO')

    if not ventas_crecimiento.empty:
        años = ventas_crecimiento['AÑO'].tolist()
        valores = ventas_crecimiento['TOTAL'].tolist()
        etiquetas = [f"S/ {v:,.2f}" for v in valores]
        filtros_activos = len(df_base) < len(st.session_state["df"])

        fig_crecimiento = go.Figure()
        fig_crecimiento.add_trace(go.Scatter(
            x=años, y=valores, mode='lines',
            line=dict(color='yellow', width=4, shape='spline'),
            fill='tozeroy', fillcolor='rgba(255,0,0,0.3)',
            hoverinfo='skip', name=''
        ))
        fig_crecimiento.add_trace(go.Scatter(
            x=años, y=valores, mode='markers+text',
            marker=dict(size=12, color='green', line=dict(width=2, color='black')),
            text=etiquetas, textposition='top center',
            textfont=dict(size=14, color='white'), name=''
        ))
        fig_crecimiento.update_layout(
            xaxis=dict(title="Año", tickmode='array', tickvals=años, ticktext=[str(a) for a in años]),
            yaxis=dict(title="Ventas Totales (S/)", tickformat=",.0f",
            range=[2_000_000, 10_000_000] if not filtros_activos else None,
            dtick=2_000_000 if not filtros_activos else None),
            plot_bgcolor='black', paper_bgcolor='black',
            font=dict(family='Segoe UI', size=16, color='white'), showlegend=False
        )
        st.plotly_chart(fig_crecimiento, use_container_width=True, key="grafico_crecimiento")
    else:
        st.info("ℹ️ No hay datos disponibles para el gráfico de comportamiento.")

    # 📉 Descenso de Ventas por Año
    st.markdown("## 📉 Descenso de Ventas por Año")
    ventas_por_año = df_base[df_base['AÑO'].isin([2023, 2024, 2025])] \
        .groupby('AÑO')['TOTAL'].sum().reset_index().sort_values('AÑO')

    if not ventas_por_año.empty and len(ventas_por_año) > 1:
        años = ventas_por_año['AÑO'].tolist()
        valores = ventas_por_año['TOTAL'].tolist()
        etiquetas = [f"S/ {v:,.2f}" for v in valores]
        porcentajes, x_intermedios, y_intermedios, flechas, colores = [], [], [], [], []
        for i in range(1, len(valores)):
            cambio = ((valores[i] - valores[i-1]) / valores[i-1] * 100) if valores[i-1] != 0 else 0
            porcentajes.append(round(cambio, 2))
            x_intermedios.append((años[i] + años[i-1]) / 2)
            y_intermedios.append((valores[i] + valores[i-1]) / 2)
            if cambio >= 0:
                flechas.append("⬆"); colores.append("lime")
            else:
                flechas.append("⬇"); colores.append("red")

        fig_descenso = go.Figure()
        fig_descenso.add_trace(go.Scatter(
            x=años, y=valores, mode='lines+markers+text', text=etiquetas, textposition='top center',
            line=dict(color='limegreen', width=4, shape='spline'),
            marker=dict(size=10, color='yellow', line=dict(width=2, color='black')),
            hoverinfo='skip', name=''
        ))
        for i in range(len(porcentajes)):
            fig_descenso.add_annotation(
                x=x_intermedios[i], y=y_intermedios[i],
                text=f"<span style='color:{colores[i]}'>{flechas[i]} {abs(porcentajes[i])}%</span>",
                showarrow=True, arrowhead=2, arrowsize=1, arrowcolor=colores[i],
                font=dict(size=14), align='center', xanchor='center', xref='x', yref='y'
            )
        filtros_activos = len(df_base) < len(st.session_state["df"])
        fig_descenso.update_layout(
            xaxis=dict(title="Año", tickmode='array', tickvals=años, ticktext=[str(a) for a in años]),
            yaxis=dict(title="Ventas Totales (S/)", tickformat=",.0f",
            range=[4_000_000, 9_000_000] if not filtros_activos else None, 
            dtick=1_000_000 if not filtros_activos else None),
            plot_bgcolor='black', paper_bgcolor='black',
            font=dict(family='Segoe UI', size=16, color='white'), showlegend=False
        )
        st.plotly_chart(fig_descenso, use_container_width=True, key="grafico_descenso")
    else:
        st.info("ℹ️ No hay suficientes datos para calcular el descenso con el contexto actual.")

    # 📈 Ventas Mensuales por Año – Comparativo 2023–2025
    st.markdown("## 📈 Ventas Mensuales por Año – Comparativo 2023–2025")
    df_3años = df_base[df_base['AÑO'].isin([2023, 2024, 2025])]
    ventas_por_mes = df_3años.groupby(['AÑO', 'MES'])['TOTAL'].sum().reset_index()

    if not ventas_por_mes.empty:
        orden_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        ventas_por_mes['MES'] = pd.Categorical(ventas_por_mes['MES'], categories=orden_meses, ordered=True)
        ventas_por_mes = ventas_por_mes.sort_values(['AÑO', 'MES'])
        colores = {2023: '#FFD700', 2024: '#FFFFFF', 2025: '#00BFFF'}
        fig_comparativo = go.Figure()
        for año_g in [2023, 2024, 2025]:
            datos_año = ventas_por_mes[ventas_por_mes['AÑO'] == año_g]
            fig_comparativo.add_trace(go.Scatter(
                x=datos_año['MES'], y=datos_año['TOTAL'],
                mode='lines+markers+text', name=f"Año {año_g}",
                line=dict(color=colores[año_g], width=3, shape='spline'),
                marker=dict(size=8, color=colores[año_g], line=dict(width=1, color='black')),
                text=[f"S/ {v:,.0f}" for v in datos_año['TOTAL']], textposition='top center'
            ))
        fig_comparativo.update_layout(
            title="📊 VENTAS REPRESENTADAS EN MESES – 2023, 2024, 2025",
            xaxis_title="Mes",
            yaxis=dict(title="Ventas Totales (S/)", tickformat=",.0f"),
            plot_bgcolor='black', paper_bgcolor='black',
            font=dict(family='Segoe UI', size=16, color='white'),
            legend=dict(title="Año", orientation="h", x=0.5, xanchor="center", y=-0.2)
        )
        st.plotly_chart(fig_comparativo, use_container_width=True, key="grafico_mensual")
    else:
        st.info("ℹ️ No hay datos mensuales con el contexto actual.")

    # 📋 Ventas Mensuales por Vendedor – Año 2025
    st.markdown("## 📋 Ventas Mensuales por Vendedor – Año 2025")
    df_2025 = df_base[(df_base['AÑO'] == 2025) & (df_base['VENDEDOR'].str.upper() != "ANULADO")]
    ventas_mensuales = df_2025.groupby(['VENDEDOR', 'MES'])['TOTAL'].sum().reset_index()

    if not ventas_mensuales.empty:
        tabla_mensual = ventas_mensuales.pivot(index='MES', columns='VENDEDOR', values='TOTAL')
        orden_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        tabla_mensual = tabla_mensual.reindex(orden_meses)
        fila_total = tabla_mensual.sum(numeric_only=True); fila_total.name = 'TOTAL'
        tabla_mensual = pd.concat([tabla_mensual, pd.DataFrame([fila_total])])
        tabla_formateada = tabla_mensual.applymap(lambda x: f"S/ {x:,.2f}" if pd.notnull(x) else "–")
        st.dataframe(
            tabla_formateada.style.set_properties(**{
                'background-color': '#ffffff', 'color': '#000000',
                'border': '1px solid #cccccc', 'font-size': '15px',
                'text-align': 'center', 'font-family': 'Segoe UI'
            }).set_caption("📆 Ventas por Vendedor por Mes – 2025 (con Totales)")
        )
    else:
        st.info("ℹ️ No hay datos de vendedores en 2025 con el contexto actual.")

    # 📊 COMPORTAMIENTO DE LAS VENTAS POR MESES POR EMPRESA – 2023, 2024, 2025
    st.markdown("## 📊 COMPORTAMIENTO DE LAS VENTAS POR MESES POR EMPRESA – 2023, 2024, 2025")
    colores_barras = {2023: '#FFD700', 2024: '#FFFFFF', 2025: '#00BFFF'}

    for empresa_actual in ['INDUSTRIAS ELECTRICAS KBA', 'TEAMWORK KBA']:
        st.markdown(f"### 🏢 {empresa_actual}")
        df_empresa = df_base[(df_base['EMPRESA'] == empresa_actual) & (df_base['AÑO'].isin([2023, 2024, 2025]))]
        resumen = df_empresa.groupby(['AÑO', 'MES'])['TOTAL'].sum().reset_index()
        if not resumen.empty:
            orden_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
            resumen['MES'] = pd.Categorical(resumen['MES'], categories=orden_meses, ordered=True)
            resumen = resumen.sort_values(['AÑO', 'MES'])
            fig_empresa = go.Figure()
            for año_g in [2023, 2024, 2025]:
                datos_año = resumen[resumen['AÑO'] == año_g]
                fig_empresa.add_trace(go.Bar(
                    x=datos_año['MES'], y=datos_año['TOTAL'],
                    name=f"Año {año_g}", marker_color=colores_barras[año_g],
                    text=[f"S/ {v:,.0f}" for v in datos_año['TOTAL']], textposition='outside'
                ))
            fig_empresa.update_layout(
                barmode='group', xaxis_title="Mes",
                yaxis=dict(title="Ventas Totales (S/)", tickformat=",.0f"),
                plot_bgcolor='black', paper_bgcolor='black',
                font=dict(family='Segoe UI', size=14, color='white'),
                legend=dict(title="Año", orientation="h", x=0.5, xanchor="center", y=-0.2)
            )
            st.plotly_chart(fig_empresa, use_container_width=True, key=f"empresa_{empresa_actual}")
        else:
            st.info(f"ℹ️ No hay datos para {empresa_actual} con el contexto actual.")

    # 🔝 Ranking de Clientes por Empresa con filtro de año
            st.markdown("## 🔝 Ranking de Clientes por Empresa")

# 🎛️ Filtro de año (aplica a ambos rankings)
            año_ranking = st.selectbox(
    "📆 Selecciona el año para ver el Top 15 clientes:",
            [2023, 2024, 2025],
            index=0
)

# 🔝 Ranking de Clientes por Empresa con filtro de año
st.markdown("## 🔝 Ranking de Clientes por Empresa")

# 🎛️ Filtro de año (aplica a ambos rankings)
año_ranking = st.selectbox(
    "📆 Selecciona el año para ver el Top 15 clientes:",
    [2023, 2024, 2025],
    index=0
)

# 🔵 TEAMWORK KBA – Ranking de Clientes
st.subheader(f"🔵 TEAMWORK KBA – Top 15 Clientes ({año_ranking})")
clientes_tw = df_base[
    (df_base['EMPRESA'] == 'TEAMWORK KBA') &
    (df_base['AÑO'] == año_ranking) &
    (df_base['CLIENTE'].str.upper() != "ANULADO")
]

if vendedor_actual != "ALL":
    clientes_tw = clientes_tw[clientes_tw['VENDEDOR'] == vendedor_actual]

clientes_tw = clientes_tw.groupby('CLIENTE', as_index=False)['TOTAL'].sum() \
    .sort_values('TOTAL', ascending=False).head(15)

if not clientes_tw.empty:
    fig_tw = px.bar(
        clientes_tw, x='TOTAL', y='CLIENTE', orientation='h',
        text=clientes_tw['TOTAL'].apply(lambda x: f"S/ {x:,.0f}"),
        template='plotly_dark', color='TOTAL'
    )
    fig_tw.update_traces(textposition='inside', textfont=dict(color='white', size=14))
    fig_tw.update_layout(
        xaxis=dict(title="Ventas Totales (S/)"),
        yaxis=dict(title="Clientes"),
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig_tw, use_container_width=True, key=f"ranking_tw_{año_ranking}")
else:
    st.info(f"ℹ️ No hay clientes para TEAMWORK KBA en {año_ranking} con el contexto actual.")


# 🔵 INDUSTRIAS ELÉCTRICAS KBA – Ranking de Clientes
st.subheader(f"🔵 INDUSTRIAS ELÉCTRICAS KBA – Top 15 Clientes ({año_ranking})")
clientes_ie = df_base[
    (df_base['EMPRESA'] == 'INDUSTRIAS ELECTRICAS KBA') &
    (df_base['AÑO'] == año_ranking) &
    (df_base['CLIENTE'].str.upper() != "ANULADO")
]

if vendedor_actual != "ALL":
    clientes_ie = clientes_ie[clientes_ie['VENDEDOR'] == vendedor_actual]

clientes_ie = clientes_ie.groupby('CLIENTE', as_index=False)['TOTAL'].sum() \
    .sort_values('TOTAL', ascending=False).head(15)

if not clientes_ie.empty:
    fig_ie = px.bar(
        clientes_ie, x='TOTAL', y='CLIENTE', orientation='h',
        text=clientes_ie['TOTAL'].apply(lambda x: f"S/ {x:,.0f}"),
        template='plotly_dark', color='TOTAL'
    )
    fig_ie.update_traces(textposition='inside', textfont=dict(color='white', size=14))
    fig_ie.update_layout(
        xaxis=dict(title="Ventas Totales (S/)"),
        yaxis=dict(title="Clientes"),
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig_ie, use_container_width=True, key=f"ranking_ie_{año_ranking}")
else:
    st.info(f"ℹ️ No hay clientes para INDUSTRIAS ELÉCTRICAS KBA en {año_ranking} con el contexto actual.")


# 📊 Totales comparativos por empresa en el año seleccionado
    st.markdown("### 📊 Totales de ventas por empresa")
    totales_empresas = df_base[df_base['AÑO'] == año_ranking].groupby('EMPRESA')['TOTAL'].sum().reset_index()
    totales_empresas['TOTAL'] = totales_empresas['TOTAL'].apply(lambda x: f"S/ {x:,.2f}")
    st.dataframe(totales_empresas.rename(columns={"EMPRESA": "Empresa", "TOTAL": "Ventas Totales"}))

# ✍️ Línea de autoría
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray;'>Aplicativo desarrollado por <b>Edward O.</b> © 2025</p>", unsafe_allow_html=True)


# 🗺️ Mapa de Provincias Atendidas
def quitar_tildes(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

st.markdown("## 🗺️ Mapa de Provincias Atendidas")
año_seleccionado = st.selectbox("📅 Selecciona el año:", [2023, 2024, 2025])

# 🔄 Preparar datos base desde el contexto
df_mapa_base = df_base.copy()
df_mapa_base['PROVINCIA'] = df_mapa_base['PROVINCIA'].astype(str).str.upper().str.strip()
df_mapa_base['DISTRITO'] = df_mapa_base['DISTRITO'].astype(str).str.upper().str.strip()
df_mapa_base['FECHA'] = pd.to_datetime(df_mapa_base['FECHA'], errors='coerce')

# 📅 Filtrar por año seleccionado
df_filtrado_mapa = df_mapa_base[df_mapa_base['FECHA'].dt.year == año_seleccionado]

# 📊 Provincias agregadas
if not df_filtrado_mapa.empty:
    provincias = df_filtrado_mapa.groupby('PROVINCIA', as_index=False)['TOTAL'].sum()
    provincias['TOTAL'] = provincias['TOTAL'].round(2)
else:
    st.warning("⚠️ No hay datos disponibles para el año seleccionado en el contexto actual.")
    provincias = pd.DataFrame(columns=['PROVINCIA', 'TOTAL'])

# 🌍 Cargar GeoJSON de provincias
try:
    with open("peru_provincias.geojson", encoding="utf-8") as f:
        geojson = json.load(f)
except Exception as e:
    st.error(f"❌ Error al cargar el mapa GeoJSON: {e}")
    geojson = None

provincia_seleccionada = st.selectbox(
    "📍 Selecciona una provincia para hacer zoom y ver distritos:",
    ["-- Selecciona una provincia --"] + list(provincias['PROVINCIA'].unique())
)

st.markdown("### 🎛️ Opciones de visualización")
quitar_filtro_mapa = st.button("🔄 Quitar filtro y ver mapa completo")

# 🗺️ Vista por provincia
if provincia_seleccionada != "-- Selecciona una provincia --" and not quitar_filtro_mapa and geojson is not None:
    try:
        with open("peru_distrital_simple.geojson", encoding="utf-8") as f:
            geojson_distritos = json.load(f)
    except Exception as e:
        st.error(f"❌ Error al cargar el GeoJSON de distritos: {e}")
        geojson_distritos = None

    if geojson_distritos is not None:
        for f in geojson_distritos['features']:
            f['properties']['NOMBDIST'] = quitar_tildes(f['properties']['NOMBDIST'].upper().strip())
            f['properties']['NOMBPROV'] = quitar_tildes(f['properties']['NOMBPROV'].upper().strip())

        provincia_geojson = quitar_tildes(provincia_seleccionada.upper().strip())
        geojson_filtrado = {
            "type": "FeatureCollection",
            "features": [
                f for f in geojson_distritos['features']
                if f['properties']['NOMBPROV'] == provincia_geojson and f['geometry'] is not None
            ]
        }

        nombres_geojson = [f['properties']['NOMBDIST'] for f in geojson_filtrado['features']]
        df_distritos = df_filtrado_mapa[df_filtrado_mapa['PROVINCIA'].str.upper().str.strip() == provincia_seleccionada.upper().strip()]
        distritos = df_distritos.groupby('DISTRITO', as_index=False)['TOTAL'].sum()

        # 🧼 Ajustes de nombres comunes
        mapeo_distritos = {
            "SURCO": "SANTIAGO DE SURCO",
            "LIMA": "CERCADO DE LIMA",
            "VILLA MARIA DEL TRIUNFO": "VILLA MARÍA DEL TRIUNFO",
            "SAN MARTIN DE PORRES": "SAN MARTÍN DE PORRES"
        }
        distritos['DISTRITO'] = distritos['DISTRITO'].replace(mapeo_distritos)
        distritos['DISTRITO'] = distritos['DISTRITO'].apply(quitar_tildes)

        distritos = pd.merge(pd.DataFrame({'DISTRITO': nombres_geojson}), distritos, on='DISTRITO', how='left')
        distritos['TOTAL'] = distritos['TOTAL'].fillna(0)
        distritos = distritos[distritos['TOTAL'] > 0]
        distritos['HOVER'] = distritos.apply(lambda row: f"{row['DISTRITO']}: S/ {row['TOTAL']:,.2f}", axis=1)

        # 🌟 Mapa distrital mejorado
        fig_mapa_distritos = px.choropleth(
        distritos, geojson=geojson_filtrado, locations='DISTRITO',
        featureidkey='properties.NOMBDIST', color='TOTAL',
        title=f"📍 Impacto Comercial en {provincia_seleccionada} – Año {año_seleccionado}",
        template='ggplot2', color_continuous_scale='Turbo',
        hover_name='HOVER', hover_data={}
)
        fig_mapa_distritos.update_geos(fitbounds="locations", visible=False)
        fig_mapa_distritos.update_traces(marker_line_width=0.5, marker_line_color='gray')
        fig_mapa_distritos.update_layout(
        paper_bgcolor='white', plot_bgcolor='white',
        font=dict(family='Segoe UI', size=16, color='black')
)

        st.plotly_chart(fig_mapa_distritos, use_container_width=True, key="mapa_distritos")

        # 📋 Tabla distritos
        st.markdown("---")
        st.markdown(f"### 📋 Distritos atendidos en {provincia_seleccionada}")
        distritos_tab = distritos.copy()
        distritos_tab['TOTAL'] = distritos_tab['TOTAL'].apply(lambda x: f"S/ {x:,.2f}")
        st.dataframe(distritos_tab.rename(columns={"DISTRITO": "Distrito", "TOTAL": "Ventas acumuladas"}))

        # 👥 Tabla clientes
        st.markdown("---")
        clientes_en_provincia = (
            df_distritos[df_distritos['DISTRITO'].apply(quitar_tildes).isin(distritos['DISTRITO'])]
            .groupby('CLIENTE', as_index=False)['TOTAL']
            .sum()
        )
        clientes_en_provincia['TOTAL'] = clientes_en_provincia['TOTAL'].apply(lambda x: f"S/ {x:,.2f}")
        st.markdown(f"### 👥 Clientes atendidos en {provincia_seleccionada} durante {año_seleccionado}")
        st.dataframe(clientes_en_provincia)

# 🗺️ Mapa general de provincias
elif geojson is not None:
    fig_mapa_provincias = px.choropleth(
        provincias, geojson=geojson, locations='PROVINCIA',
        featureidkey='properties.NOMBPROV', color='TOTAL',
        title=f"📍 Cobertura Comercial en el Perú – Año {año_seleccionado}",
        template='ggplot2', color_continuous_scale='Turbo',
        hover_name='PROVINCIA', hover_data={'TOTAL': True}
    )
    fig_mapa_provincias.update_geos(fitbounds="locations", visible=False)
    fig_mapa_provincias.update_traces(marker_line_width=0.5, marker_line_color='black')
    fig_mapa_provincias.update_layout(
        margin={"r": 0, "t": 60, "l": 0, "b": 0},
        paper_bgcolor='white', plot_bgcolor='white',
        font=dict(family='Segoe UI', size=18, color='black'),
        coloraxis_colorbar=dict(
        title="Ventas (S/)", tickprefix="S/ ",
        thickness=20, len=0.8, bgcolor='rgba(0,0,0,0)', outlinewidth=0,
        tickfont=dict(color='black', size=14)
    )
)

    st.plotly_chart(fig_mapa_provincias, use_container_width=True, key="mapa_provincias")

    # 📋 Leyenda de provincias
    st.markdown("---")
    st.markdown("### 📍 Provincias con atención comercial")
    tabla_leyenda = provincias[['PROVINCIA', 'TOTAL']].copy()
    tabla_leyenda['TOTAL'] = tabla_leyenda['TOTAL'].apply(lambda x: f"S/ {x:,.2f}")
    st.dataframe(tabla_leyenda.rename(columns={"PROVINCIA": "Provincia", "TOTAL": "Ventas acumuladas"}))

else:
    st.warning("⚠️ No hay datos disponibles para el año seleccionado.")
