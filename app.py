# 📦 Importar librerías
import os
import json
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import unicodedata

st.markdown(
    """
    <link rel="manifest" href="manifest.json">
    <script>
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('service-worker.js');
      }
    </script>
    """,
    unsafe_allow_html=True
)

# 🔐 Usuarios y roles (asegurando coincidencia exacta con df['VENDEDOR'])
USUARIOS = {
    "admin": {"password": "admin", "vendedor": "ALL"},
    "Guillermo": {"password": "47835765", "vendedor": "GUILLERMO"},
    "JorgeChavez": {"password": "17895862", "vendedor": "JORGE CHAVEZ"},  # corregido
    "JoseCarlos": {"password": "77298007", "vendedor": "JOSE CARLOS"},
    "MariaJanet": {"password": "76029937", "vendedor": "MARIA JANET"},
    "Milena": {"password": "09668821", "vendedor": "MILENA"},
    "WalterBejarano": {"password": "30857970", "vendedor": "WALTER BEJARANO"},
    "YeseniaFlores": {"password": "40368177", "vendedor": "YESENIA FLORES"},
}

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
                <h3 style='color:white;margin-top:0;'>2023 – 2026</h3>  <!-- MODIFICADO PARA 2026 -->
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

    col1, col2, col3, col4 = st.columns([3, 3, 3, 3])

    with col1:
        activar_filtro_mes = st.checkbox("📅 Filtrar por mes", value=False)
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
        activar_filtro_año = st.checkbox("📆 Filtrar por año", value=False)
        if activar_filtro_año:
            año = st.selectbox(
                label="Año",
                options=[2023, 2024, 2025, 2026],  # MODIFICADO PARA 2026
                format_func=lambda x: f"Año {x}",
                placeholder="Selecciona año",
                label_visibility="visible"
            )
        else:
            año = None

    with col3:
        activar_filtro_empresa = st.checkbox("🏢 Filtrar por empresa", value=False)
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
        activar_filtro_vendedor = st.checkbox("🧑‍💼 Filtrar por vendedor", value=False)
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
    st.markdown("## 📋 Ventas Totales por Año – 2 Mercados (Lima y Provincias)")
    ventas_tabla = df_base[df_base['AÑO'].isin([2023, 2024, 2025, 2026])].groupby(['EMPRESA', 'AÑO'])['TOTAL'].sum().reset_index()

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
            }).set_caption("💼 Comparativo de Ventas Totales por Año (2023–2026)")  # MODIFICADO PARA 2026
        )
    else:
        st.info("ℹ️ No hay datos para el comparativo con el contexto actual.")

    # 📈 Comportamiento de las Ventas 2023–2026  # MODIFICADO PARA 2026
    st.markdown("## 📈 Comportamiento de las Ventas 2023–2026")
    ventas_crecimiento = df_base[df_base['AÑO'].isin([2023, 2024, 2025, 2026])].groupby('AÑO')['TOTAL'].sum().reset_index().sort_values('AÑO')

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
    ventas_por_año = df_base[df_base['AÑO'].isin([2023, 2024, 2025, 2026])].groupby('AÑO')['TOTAL'].sum().reset_index().sort_values('AÑO')

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

    # 📈 Ventas Mensuales por Año – Comparativo 2023–2026  # MODIFICADO PARA 2026
    st.markdown("## 📈 Ventas Mensuales por Año – Comparativo 2023–2026")
    df_4años = df_base[df_base['AÑO'].isin([2023, 2024, 2025, 2026])]  # MODIFICADO PARA 2026
    ventas_por_mes = df_4años.groupby(['AÑO', 'MES'])['TOTAL'].sum().reset_index()

    if not ventas_por_mes.empty:
        orden_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        ventas_por_mes['MES'] = pd.Categorical(ventas_por_mes['MES'], categories=orden_meses, ordered=True)
        ventas_por_mes = ventas_por_mes.sort_values(['AÑO', 'MES'])
        colores = {2023: '#FFD700', 2024: '#FFFFFF', 2025: '#00BFFF', 2026: '#FF69B4'}  # MODIFICADO PARA 2026 (rosa para 2026)
        fig_comparativo = go.Figure()
        for año_g in [2023, 2024, 2025, 2026]:  # MODIFICADO PARA 2026
            datos_año = ventas_por_mes[ventas_por_mes['AÑO'] == año_g]
            fig_comparativo.add_trace(go.Scatter(
                x=datos_año['MES'], y=datos_año['TOTAL'],
                mode='lines+markers+text', name=f"Año {año_g}",
                line=dict(color=colores[año_g], width=3, shape='spline'),
                marker=dict(size=8, color=colores[año_g], line=dict(width=1, color='black')),
                text=[f"S/ {v:,.0f}" for v in datos_año['TOTAL']], textposition='top center'
            ))
        fig_comparativo.update_layout(
            title="📊 VENTAS REPRESENTADAS EN MESES – 2023, 2024, 2025, 2026",  # MODIFICADO PARA 2026
            xaxis_title="Mes",
            yaxis=dict(title="Ventas Totales (S/)", tickformat=",.0f"),
            plot_bgcolor='black', paper_bgcolor='black',
            font=dict(family='Segoe UI', size=16, color='white'),
            legend=dict(title="Año", orientation="h", x=0.5, xanchor="center", y=-0.2)
        )
        st.plotly_chart(fig_comparativo, use_container_width=True, key="grafico_mensual")
    else:
        st.info("ℹ️ No hay datos mensuales con el contexto actual.")

    # 📋 Ventas Mensuales por Vendedor – Selector de Año  # MEJORADO
    st.markdown("## 📋 Ventas Mensuales por Vendedor")
    año_vendedor = st.selectbox(
        "Seleccionar año para ventas por vendedor:", 
        [2023, 2024, 2025, 2026],  # MODIFICADO PARA 2026
        index=2,  # Por defecto 2025
        key="selector_año_vendedor"
    )
    
    df_año_vendedor = df_base[(df_base['AÑO'] == año_vendedor) & (df_base['VENDEDOR'].str.upper() != "ANULADO")]
    ventas_mensuales = df_año_vendedor.groupby(['VENDEDOR', 'MES'])['TOTAL'].sum().reset_index()

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
            }).set_caption(f"📆 Ventas por Vendedor por Mes – {año_vendedor} (con Totales)")  # MODIFICADO PARA DINÁMICO
        )
    else:
        st.info(f"ℹ️ No hay datos de vendedores en {año_vendedor} con el contexto actual.")

    # 📊 COMPORTAMIENTO DE LAS VENTAS POR MESES POR EMPRESA – 2023, 2024, 2025, 2026  # MODIFICADO PARA 2026
    st.markdown("## 📊 COMPORTAMIENTO DE LAS VENTAS POR MESES POR EMPRESA – 2023, 2024, 2025, 2026")
    colores_barras = {2023: '#FFD700', 2024: '#FFFFFF', 2025: '#00BFFF', 2026: '#FF69B4'}  # MODIFICADO PARA 2026

    for empresa_actual in ['INDUSTRIAS ELECTRICAS KBA', 'TEAMWORK KBA']:
        st.markdown(f"### 🏢 {empresa_actual}")
        df_empresa = df_base[(df_base['EMPRESA'] == empresa_actual) & (df_base['AÑO'].isin([2023, 2024, 2025, 2026]))]  # MODIFICADO PARA 2026
        resumen = df_empresa.groupby(['AÑO', 'MES'])['TOTAL'].sum().reset_index()
        if not resumen.empty:
            orden_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
            resumen['MES'] = pd.Categorical(resumen['MES'], categories=orden_meses, ordered=True)
            resumen = resumen.sort_values(['AÑO', 'MES'])
            fig_empresa = go.Figure()
            for año_g in [2023, 2024, 2025, 2026]:  # MODIFICADO PARA 2026
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

    # 🎛️ Filtro de año (aplica a ambos rankings) - MODIFICADO PARA 2026
    año_ranking = st.selectbox(
        "📆 Selecciona el año para ver el Top 15 clientes:",
        [2023, 2024, 2025, 2026],  # MODIFICADO PARA 2026
        index=0,
        key="selector_año_ranking"
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

# =============================================================================
# 🆕 NUEVA SECCIÓN 1: COMPARADOR AVANZADO (SOLO PARA ADMIN)
# =============================================================================
if vendedor_actual == "ALL":  # Solo visible para ADMIN
    st.markdown("---")
    st.markdown("## 🎯 COMPARADOR AVANZADO (ADMIN)")
    st.markdown("### Personaliza tu comparación y visualiza los resultados")
    
    # Crear pestañas dentro del comparador
    tab1, tab2 = st.tabs(["📊 Configurar Comparación", "📋 Ver Datos Detallados"])
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📌 Eje X (Categorías)**")
            eje_x = st.selectbox(
                "Selecciona qué quieres comparar:",
                options=["PROVINCIA", "VENDEDOR", "AÑO", "MES", "EMPRESA"],
                index=0,
                key="comparador_eje_x"
            )
        
        with col2:
            st.markdown("**🎨 Agrupar por (Color)**")
            agrupar_por = st.selectbox(
                "Selecciona el grupo de comparación:",
                options=["AÑO", "VENDEDOR", "PROVINCIA", "MES", "EMPRESA", "NINGUNO"],
                index=0,
                key="comparador_agrupar"
            )
        
        with col3:
            st.markdown("**📏 Métrica a visualizar**")
            metrica = st.selectbox(
                "Selecciona la métrica:",
                options=["TOTAL (Suma de ventas)", "Cantidad de operaciones"],
                index=0,
                key="comparador_metrica"
            )
        
        # Filtros adicionales para el comparador
        st.markdown("#### 🔍 Filtros adicionales para la comparación")
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            años_disponibles = sorted(df_base['AÑO'].dropna().unique())
            años_comp = st.multiselect(
                "Años a incluir:",
                options=años_disponibles,
                default=años_disponibles,
                key="filtro_años_comparador"
            )
        
        with col_f2:
            empresas_comp = st.multiselect(
                "Empresas:",
                options=['INDUSTRIAS ELECTRICAS KBA', 'TEAMWORK KBA'],
                default=['INDUSTRIAS ELECTRICAS KBA', 'TEAMWORK KBA'],
                key="filtro_empresas_comparador"
            )
        
        with col_f3:
            if eje_x != "VENDEDOR" and agrupar_por != "VENDEDOR":
                vendedores_comp = st.multiselect(
                    "Vendedores:",
                    options=sorted(df_base['VENDEDOR'].unique()),
                    default=[],
                    key="filtro_vendedores_comparador"
                )
            else:
                vendedores_comp = []
                st.info("ℹ️ Vendedor ya está en ejes/grupos")
        
        # Aplicar filtros
        df_comp = df_base.copy()
        if años_comp:
            df_comp = df_comp[df_comp['AÑO'].isin(años_comp)]
        if empresas_comp:
            df_comp = df_comp[df_comp['EMPRESA'].isin(empresas_comp)]
        if vendedores_comp:
            df_comp = df_comp[df_comp['VENDEDOR'].isin(vendedores_comp)]
        
        # Preparar datos según métrica seleccionada
        if metrica == "TOTAL (Suma de ventas)":
            if agrupar_por != "NINGUNO":
                df_group = df_comp.groupby([eje_x, agrupar_por], as_index=False)['TOTAL'].sum()
            else:
                df_group = df_comp.groupby([eje_x], as_index=False)['TOTAL'].sum()
            titulo_metrica = "Ventas Totales (S/)"
            formato = "S/ {:,.0f}"
        else:  # Cantidad de operaciones
            if agrupar_por != "NINGUNO":
                df_group = df_comp.groupby([eje_x, agrupar_por], as_index=False).size().rename(columns={'size': 'CANTIDAD'})
            else:
                df_group = df_comp.groupby([eje_x], as_index=False).size().rename(columns={'size': 'CANTIDAD'})
            titulo_metrica = "Número de Operaciones"
            formato = "{:,.0f} ops"
        
        # Crear gráfico
        if not df_group.empty:
            if agrupar_por != "NINGUNO":
                # Gráfico de barras agrupadas
                fig_comp = px.bar(
                    df_group, 
                    x=eje_x, 
                    y=df_group.columns[-1],  # La última columna es TOTAL o CANTIDAD
                    color=agrupar_por,
                    barmode='group',
                    title=f"Comparación: {eje_x} por {agrupar_por}",
                    labels={eje_x: eje_x.title(), df_group.columns[-1]: titulo_metrica, agrupar_por: agrupar_por.title()},
                    text_auto=True,
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                fig_comp.update_traces(textposition='outside', textfont=dict(size=11))
                
                # Crear tabla pivote
                tabla_pivot = df_group.pivot(index=eje_x, columns=agrupar_por, values=df_group.columns[-1]).fillna(0)
                
            else:
                # Gráfico de barras simple
                fig_comp = px.bar(
                    df_group, 
                    x=eje_x, 
                    y=df_group.columns[-1],
                    title=f"Comparación por {eje_x}",
                    labels={eje_x: eje_x.title(), df_group.columns[-1]: titulo_metrica},
                    text_auto=True,
                    color_discrete_sequence=['#3366CC']
                )
                fig_comp.update_traces(textposition='outside', textfont=dict(size=11))
                tabla_pivot = df_group.set_index(eje_x)
            
            # Mejorar diseño del gráfico
            fig_comp.update_layout(
                xaxis_title=eje_x.title(),
                yaxis_title=titulo_metrica,
                plot_bgcolor='rgba(0,0,0,0.05)',
                paper_bgcolor='white',
                font=dict(family='Segoe UI', size=14),
                legend_title=agrupar_por.title() if agrupar_por != "NINGUNO" else "",
                height=600,
                margin=dict(l=50, r=50, t=80, b=80)
            )
            
            # Mostrar gráfico
            st.plotly_chart(fig_comp, use_container_width=True, key="grafico_comparador")
            
            # Mostrar tabla resumen
            st.markdown("#### 📊 Tabla comparativa")
            
            # Formatear tabla
            tabla_formateada = tabla_pivot.copy()
            for col in tabla_formateada.columns:
                if metrica == "TOTAL (Suma de ventas)":
                    tabla_formateada[col] = tabla_formateada[col].apply(lambda x: f"S/ {x:,.2f}")
                else:
                    tabla_formateada[col] = tabla_formateada[col].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(
                tabla_formateada,
                use_container_width=True,
                height=400
            )
            
            # Botón para exportar tabla
            csv = tabla_pivot.to_csv().encode('utf-8')
            st.download_button(
                label="📥 Descargar tabla comparativa (CSV)",
                data=csv,
                file_name=f"comparacion_{eje_x}_vs_{agrupar_por}.csv",
                mime="text/csv",
                key="btn_descargar_comparador"
            )
        else:
            st.warning("⚠️ No hay datos con los filtros seleccionados")
    
    with tab2:
        st.markdown("### 📋 Datos detallados de la comparación")
        
        # Selector de nivel de detalle
        nivel_detalle = st.radio(
            "Nivel de detalle:",
            ["Resumen por grupo", "Todos los registros"],
            horizontal=True,
            key="nivel_detalle_comparador"
        )
        
        if nivel_detalle == "Resumen por grupo":
            # Mostrar el dataframe agrupado
            if 'df_group' in locals() and not df_group.empty:
                df_show = df_group.copy()
                if metrica == "TOTAL (Suma de ventas)":
                    df_show['TOTAL'] = df_show['TOTAL'].apply(lambda x: f"S/ {x:,.2f}")
                else:
                    df_show['CANTIDAD'] = df_show['CANTIDAD'].apply(lambda x: f"{x:,.0f}")
                st.dataframe(df_show, use_container_width=True)
        else:
            # Mostrar todos los registros filtrados
            df_detalle = df_comp[['FECHA', 'VENDEDOR', 'EMPRESA', 'CLIENTE', 'PROVINCIA', 'DISTRITO', 'TOTAL', 'AÑO', 'MES']].copy()
            df_detalle['TOTAL'] = df_detalle['TOTAL'].apply(lambda x: f"S/ {x:,.2f}")
            st.dataframe(df_detalle, use_container_width=True, height=500)
            
            # Botón para exportar detalle
            csv_detalle = df_comp.to_csv().encode('utf-8')
            st.download_button(
                label="📥 Exportar todos los registros filtrados (CSV)",
                data=csv_detalle,
                file_name="registros_filtrados.csv",
                mime="text/csv",
                key="btn_descargar_detalle"
            )

# =============================================================================
# 🆕 NUEVA SECCIÓN 2: EXPORTACIÓN DE DATOS PARA TODOS LOS USUARIOS
# =============================================================================
st.markdown("---")
st.markdown("## 📤 EXPORTACIÓN DE DATOS")

# Crear pestañas para las diferentes exportaciones
tab_exp1, tab_exp2, tab_exp3 = st.tabs(["📊 Mis Ventas", "👥 Mis Clientes", "⚙️ Exportación Avanzada"])

with tab_exp1:
    st.markdown("### 📊 Exportar mis ventas")
    st.markdown(f"**Usuario actual:** {usuario} | **Vista:** {'Todos los vendedores' if vendedor_actual == 'ALL' else vendedor_actual}")
    
    # Filtros para la exportación
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        año_export = st.selectbox(
            "Seleccionar año:",
            options=["Todos"] + [2023, 2024, 2025, 2026],
            index=0,
            key="año_export_ventas"
        )
    
    with col_f2:
        empresa_export = st.selectbox(
            "Seleccionar empresa:",
            options=["Todas", "INDUSTRIAS ELECTRICAS KBA", "TEAMWORK KBA"],
            index=0,
            key="empresa_export_ventas"
        )
    
    # Aplicar filtros
    df_export_ventas = df.copy()
    
    if año_export != "Todos":
        df_export_ventas = df_export_ventas[df_export_ventas['AÑO'] == año_export]
    
    if empresa_export != "Todas":
        df_export_ventas = df_export_ventas[df_export_ventas['EMPRESA'] == empresa_export]
    
    # Seleccionar columnas relevantes
    columnas_ventas = ['FECHA', 'VENDEDOR', 'EMPRESA', 'CLIENTE', 'PROVINCIA', 'DISTRITO', 'TOTAL', 'AÑO', 'MES']
    df_export_ventas = df_export_ventas[columnas_ventas].copy()
    
    # Mostrar preview
    st.markdown(f"**📋 Vista previa ({len(df_export_ventas)} registros):**")
    df_preview = df_export_ventas.head(10).copy()
    df_preview['TOTAL'] = df_preview['TOTAL'].apply(lambda x: f"S/ {x:,.2f}")
    st.dataframe(df_preview, use_container_width=True)
    
    if len(df_export_ventas) > 10:
        st.caption(f"Mostrando 10 de {len(df_export_ventas)} registros")
    
    # Botón de exportación
    if not df_export_ventas.empty:
        # Crear archivo Excel
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_export_ventas.to_excel(writer, sheet_name='Ventas', index=False)
            
            # Formato para moneda
            workbook = writer.book
            worksheet = writer.sheets['Ventas']
            money_format = workbook.add_format({'num_format': 'S/ #,##0.00'})
            worksheet.set_column('G:G', 15, money_format)  # Columna TOTAL
            
            # Ajustar ancho de columnas
            worksheet.set_column('A:A', 12)  # FECHA
            worksheet.set_column('B:B', 15)  # VENDEDOR
            worksheet.set_column('C:C', 25)  # EMPRESA
            worksheet.set_column('D:D', 30)  # CLIENTE
            worksheet.set_column('E:E', 15)  # PROVINCIA
            worksheet.set_column('F:F', 15)  # DISTRITO
            worksheet.set_column('H:H', 8)   # AÑO
            worksheet.set_column('I:I', 8)   # MES
        
        st.download_button(
            label="📥 DESCARGAR MIS VENTAS EN EXCEL",
            data=output.getvalue(),
            file_name=f"mis_ventas_{usuario}_{año_export}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="btn_export_ventas",
            use_container_width=True
        )
    else:
        st.warning("No hay ventas para exportar con los filtros seleccionados.")

with tab_exp2:
    st.markdown("### 👥 Exportar mis clientes")
    st.markdown("Listado de clientes únicos con el total de ventas acumulado")
    
    # Filtros para clientes
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        año_clientes = st.selectbox(
            "Año para clientes:",
            options=["Todos los años"] + [2023, 2024, 2025, 2026],
            index=0,
            key="año_export_clientes"
        )
    
    with col_c2:
        min_venta = st.number_input(
            "Venta mínima (S/):",
            min_value=0,
            value=0,
            step=100,
            key="min_venta_clientes"
        )
    
    # Filtrar datos
    df_clientes = df.copy()
    
    if año_clientes != "Todos los años":
        df_clientes = df_clientes[df_clientes['AÑO'] == año_clientes]
    
    # Agrupar por cliente
    clientes_resumen = df_clientes.groupby(['CLIENTE', 'VENDEDOR', 'EMPRESA']).agg({
        'TOTAL': 'sum',
        'FECHA': 'count'
    }).rename(columns={'FECHA': 'CANTIDAD_COMPRAS'}).reset_index()
    
    # Filtrar por venta mínima
    clientes_resumen = clientes_resumen[clientes_resumen['TOTAL'] >= min_venta]
    clientes_resumen = clientes_resumen.sort_values('TOTAL', ascending=False)
    
    # Calcular porcentaje
    total_ventas = clientes_resumen['TOTAL'].sum()
    clientes_resumen['% PARTICIPACIÓN'] = (clientes_resumen['TOTAL'] / total_ventas * 100).round(2)
    
    # Mostrar preview
    st.markdown(f"**📋 Vista previa - Top 10 clientes ({len(clientes_resumen)} clientes en total):**")
    df_clientes_preview = clientes_resumen.head(10).copy()
    df_clientes_preview['TOTAL'] = df_clientes_preview['TOTAL'].apply(lambda x: f"S/ {x:,.2f}")
    df_clientes_preview['% PARTICIPACIÓN'] = df_clientes_preview['% PARTICIPACIÓN'].apply(lambda x: f"{x}%")
    st.dataframe(df_clientes_preview, use_container_width=True)
    
    # Botones de exportación
    if not clientes_resumen.empty:
        col_b1, col_b2 = st.columns(2)
        
        with col_b1:
            # Exportar a Excel
            output_clientes = io.BytesIO()
            with pd.ExcelWriter(output_clientes, engine='xlsxwriter') as writer:
                clientes_resumen.to_excel(writer, sheet_name='Clientes', index=False)
                
                workbook = writer.book
                worksheet = writer.sheets['Clientes']
                
                # Formatos
                money_format = workbook.add_format({'num_format': 'S/ #,##0.00'})
                percent_format = workbook.add_format({'num_format': '0.00%'})
                
                worksheet.set_column('D:D', 15, money_format)  # TOTAL
                worksheet.set_column('F:F', 12, percent_format)  # % PARTICIPACIÓN
                worksheet.set_column('A:A', 35)  # CLIENTE
                worksheet.set_column('B:B', 15)  # VENDEDOR
                worksheet.set_column('C:C', 25)  # EMPRESA
                worksheet.set_column('E:E', 12)  # CANTIDAD_COMPRAS
            
            st.download_button(
                label="📥 EXCEL - Lista de clientes",
                data=output_clientes.getvalue(),
                file_name=f"mis_clientes_{usuario}_{año_clientes}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="btn_export_clientes_excel"
            )
        
        with col_b2:
            # Exportar a CSV
            csv_clientes = clientes_resumen.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 CSV - Lista de clientes",
                data=csv_clientes,
                file_name=f"mis_clientes_{usuario}_{año_clientes}.csv",
                mime="text/csv",
                key="btn_export_clientes_csv"
            )
    else:
        st.warning("No hay clientes que cumplan los criterios.")

with tab_exp3:
    st.markdown("### ⚙️ Exportación Avanzada")
    st.markdown("Personaliza los campos a exportar")
    
    # Selección de columnas
    todas_columnas = df.columns.tolist()
    columnas_seleccionadas = st.multiselect(
        "Selecciona las columnas a exportar:",
        options=todas_columnas,
        default=['FECHA', 'VENDEDOR', 'EMPRESA', 'CLIENTE', 'PROVINCIA', 'DISTRITO', 'TOTAL'],
        key="columnas_avanzado"
    )
    
    if columnas_seleccionadas:
        df_avanzado = df[columnas_seleccionadas].copy()
        
        # Filtro rápido
        st.markdown("**🔍 Filtro rápido (por texto en cualquier columna):**")
        filtro_texto = st.text_input("Buscar...", key="filtro_avanzado")
        
        if filtro_texto:
            mask = df_avanzado.astype(str).apply(lambda x: x.str.contains(filtro_texto, case=False, na=False)).any(axis=1)
            df_avanzado = df_avanzado[mask]
        
        st.markdown(f"**Total registros: {len(df_avanzado)}**")
        
        if not df_avanzado.empty:
            # Preview
            st.dataframe(df_avanzado.head(20), use_container_width=True)
            
            # Exportar
            csv_avanzado = df_avanzado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 DESCARGAR EXTRACTO PERSONALIZADO (CSV)",
                data=csv_avanzado,
                file_name=f"exportacion_personalizada_{usuario}.csv",
                mime="text/csv",
                key="btn_export_avanzado",
                use_container_width=True
            )



# ✍️ Línea de autoría
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray;'>Aplicativo desarrollado por <b>Edward O.</b> © 2025</p>", unsafe_allow_html=True)



# 🗺️ Mapa de Provincias Atendidas
def quitar_tildes(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

st.markdown("## 🗺️ Mapa de Provincias Atendidas")
# MODIFICADO PARA 2026
año_seleccionado = st.selectbox("📅 Selecciona el año:", [2023, 2024, 2025, 2026], key="selector_año_mapa")

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
    ["-- Selecciona una provincia --"] + list(provincias['PROVINCIA'].unique()),
    key="selector_provincia_mapa"
)

st.markdown("### 🎛️ Opciones de visualización")
quitar_filtro_mapa = st.button("🔄 Quitar filtro y ver mapa completo", key="boton_quitar_filtro_mapa")

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
