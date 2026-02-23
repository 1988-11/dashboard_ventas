# 📦 Importar librerías
import os
import json
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import unicodedata
import io  # Para manejo de archivos en memoria

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
# 🆕 NUEVA SECCIÓN 1: COMPARADOR AVANZADO PROFESIONAL (SOLO PARA ADMIN)
# =============================================================================
import io  # Asegúrate de tener esto al inicio del archivo

if vendedor_actual == "ALL":  # Solo visible para ADMIN
    st.markdown("---")
    st.markdown("## 🎯 COMPARADOR AVANZADO PROFESIONAL")
    st.markdown("### Análisis comparativo con visualizaciones profesionales")
    
    # Estilo profesional para el comparador
    st.markdown("""
    <style>
    .comparador-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #003366;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        border-bottom: 3px solid #003366;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Crear pestañas profesionales
    tab_comp1, tab_comp2, tab_comp3, tab_comp4 = st.tabs([
        "📊 Comparador General", 
        "🏙️ Comparador por Distritos", 
        "📈 Análisis de Tendencias",
        "📋 Datos Detallados"
    ])
    
    # ==============================================
    # PESTAÑA 1: COMPARADOR GENERAL MEJORADO
    # ==============================================
    with tab_comp1:
        st.markdown('<div class="comparador-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Panel de Control de Comparaciones")
        
        # Diseño profesional en 3 columnas
        col_param1, col_param2, col_param3 = st.columns(3)
        
        with col_param1:
            st.markdown("**📌 EJE PRINCIPAL**")
            eje_x = st.selectbox(
                "Selecciona la dimensión principal:",
                options=[
                    "🏢 EMPRESA", 
                    "🧑 VENDEDOR", 
                    "📍 PROVINCIA", 
                    "🏘️ DISTRITO", 
                    "📆 AÑO", 
                    "📅 MES"
                ],
                index=0,
                key="prof_eje_x",
                help="Selecciona qué quieres analizar en el eje X"
            )
            # Limpiar el emoji para el nombre real de la columna
            eje_x_real = eje_x.split(" ")[1] if " " in eje_x else eje_x
        
        with col_param2:
            st.markdown("**🎨 AGRUPAR POR**")
            agrupar_por = st.selectbox(
                "Selecciona el grupo comparativo:",
                options=[
                    "📆 AÑO", 
                    "🧑 VENDEDOR", 
                    "🏢 EMPRESA", 
                    "📍 PROVINCIA",
                    "🏘️ DISTRITO",
                    "📅 MES",
                    "⚪ SIN AGRUPAR"
                ],
                index=0,
                key="prof_agrupar",
                help="Agrupa los datos para comparar"
            )
            agrupar_real = agrupar_por.split(" ")[1] if " " in agrupar_por and agrupar_por != "⚪ SIN AGRUPAR" else "NINGUNO"
        
        with col_param3:
            st.markdown("**📏 MÉTRICA**")
            metrica = st.radio(
                "Selecciona la métrica:",
                options=["💰 Ventas Totales", "📊 Cantidad de Operaciones", "🎯 Ticket Promedio"],
                horizontal=False,
                key="prof_metrica",
                help="Elige qué medir"
            )
        
        # Filtros avanzados
        st.markdown("#### 🔍 FILTROS AVANZADOS")
        col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)
        
        with col_filtro1:
            años_prof = sorted(df_base['AÑO'].dropna().unique())
            años_sel = st.multiselect(
                "📆 Años",
                options=años_prof,
                default=años_prof,
                key="prof_años"
            )
        
        with col_filtro2:
            empresas_prof = ['INDUSTRIAS ELECTRICAS KBA', 'TEAMWORK KBA']
            empresas_sel = st.multiselect(
                "🏢 Empresas",
                options=empresas_prof,
                default=empresas_prof,
                key="prof_empresas"
            )
        
        with col_filtro3:
            # Provincias disponibles filtradas por otros criterios
            provincias_prof = sorted(df_base[df_base['AÑO'].isin(años_sel) & 
                                              df_base['EMPRESA'].isin(empresas_sel)]['PROVINCIA'].unique())
            provincias_sel = st.multiselect(
                "📍 Provincias",
                options=provincias_prof,
                default=[],
                key="prof_provincias"
            )
        
        with col_filtro4:
            # Vendedores disponibles
            vendedores_prof = sorted(df_base[df_base['AÑO'].isin(años_sel) & 
                                              df_base['EMPRESA'].isin(empresas_sel)]['VENDEDOR'].unique())
            vendedores_sel = st.multiselect(
                "🧑 Vendedores",
                options=vendedores_prof,
                default=[],
                key="prof_vendedores"
            )
        
        # Aplicar filtros
        df_prof = df_base.copy()
        df_prof = df_prof[df_prof['AÑO'].isin(años_sel)]
        df_prof = df_prof[df_prof['EMPRESA'].isin(empresas_sel)]
        
        if provincias_sel:
            df_prof = df_prof[df_prof['PROVINCIA'].isin(provincias_sel)]
        if vendedores_sel:
            df_prof = df_prof[df_prof['VENDEDOR'].isin(vendedores_sel)]
        
        # Calcular métricas
        if metrica == "💰 Ventas Totales":
            valor_col = 'TOTAL'
            titulo_metrica = "Ventas Totales (S/)"
            formato = "S/ {:,.0f}"
            if agrupar_real != "NINGUNO":
                df_group = df_prof.groupby([eje_x_real, agrupar_real], as_index=False)[valor_col].sum()
            else:
                df_group = df_prof.groupby([eje_x_real], as_index=False)[valor_col].sum()
        
        elif metrica == "📊 Cantidad de Operaciones":
            valor_col = 'CANTIDAD'
            titulo_metrica = "Número de Operaciones"
            formato = "{:,.0f} ops"
            if agrupar_real != "NINGUNO":
                df_group = df_prof.groupby([eje_x_real, agrupar_real]).size().reset_index(name='CANTIDAD')
            else:
                df_group = df_prof.groupby([eje_x_real]).size().reset_index(name='CANTIDAD')
        
        else:  # Ticket Promedio
            valor_col = 'TOTAL'
            titulo_metrica = "Ticket Promedio (S/)"
            formato = "S/ {:,.0f}"
            if agrupar_real != "NINGUNO":
                df_group = df_prof.groupby([eje_x_real, agrupar_real]).agg(
                    TOTAL=('TOTAL', 'mean')
                ).reset_index()
            else:
                df_group = df_prof.groupby([eje_x_real]).agg(
                    TOTAL=('TOTAL', 'mean')
                ).reset_index()
        
        # Métricas de resumen
        if not df_prof.empty:
            st.markdown("#### 📈 RESUMEN EJECUTIVO")
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            
            with col_m1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                total_ventas = df_prof['TOTAL'].sum()
                st.metric("💵 Ventas Totales", f"S/ {total_ventas:,.0f}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_m2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                num_ops = len(df_prof)
                st.metric("📦 Operaciones", f"{num_ops:,}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_m3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                ticket_prom = total_ventas / num_ops if num_ops > 0 else 0
                st.metric("🎫 Ticket Promedio", f"S/ {ticket_prom:,.0f}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_m4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                num_clientes = df_prof['CLIENTE'].nunique()
                st.metric("👥 Clientes Únicos", f"{num_clientes:,}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # GRÁFICO PROFESIONAL CON EJES LEGIBLES
        if not df_group.empty:
            st.markdown("#### 📊 VISUALIZACIÓN PROFESIONAL")
            
            # 🔥 MEJORA 1: Convertir años a string para evitar decimales
            if eje_x_real == 'AÑO':
                df_group['AÑO'] = df_group['AÑO'].astype(int).astype(str)
            if agrupar_real == 'AÑO' and agrupar_real != "NINGUNO":
                df_group['AÑO'] = df_group['AÑO'].astype(int).astype(str)
            
            if agrupar_real != "NINGUNO":
     # Gráfico de barras agrupado profesional - VERSIÓN MEJORADA
                fig_prof = px.bar(
                    df_group, 
                    x=eje_x_real, 
                    y=df_group.columns[-1],
                    color=agrupar_real,
                    barmode='group',
                    title=f"<b>Comparación: {eje_x_real.title()} por {agrupar_real.title()}</b>",
                    labels={
                        eje_x_real: eje_x_real.title(), 
                        df_group.columns[-1]: titulo_metrica, 
                        agrupar_real: agrupar_real.title()
                    },
                    text_auto=True,
                    color_discrete_sequence=px.colors.qualitative.Plotly,
                    template='plotly_white'
                )
                
                # Personalización profesional MEJORADA
                fig_prof.update_traces(
                    textposition='outside',
                    textfont=dict(size=12, family='Arial Black', color='black'),  # 🔥 NEGRO Y NEGRITA
                    marker_line_width=1.5,
                    marker_line_color='black',
                    texttemplate='%{text:,.0f}'
                )
                
                # Tabla pivote
                tabla_pivot = df_group.pivot(
                    index=eje_x_real, 
                    columns=agrupar_real, 
                    values=df_group.columns[-1]
                ).fillna(0)
                
            else:
                # Gráfico de barras simple profesional - VERSIÓN MEJORADA
                fig_prof = px.bar(
                    df_group, 
                    x=eje_x_real, 
                    y=df_group.columns[-1],
                    title=f"<b>Análisis por {eje_x_real.title()}</b>",
                    labels={eje_x_real: eje_x_real.title(), df_group.columns[-1]: titulo_metrica},
                    text_auto=True,
                    color_discrete_sequence=['#003366'],
                    template='plotly_white'
                )
                fig_prof.update_traces(
                    textposition='outside',
                    textfont=dict(size=12, family='Arial Black', color='white'),  # 🔥 BLANCO NEGRITA
                    marker_line_width=1.5,
                    marker_line_color='white',
                    marker_color='#003366',
                    texttemplate='%{text:,.0f}'
                )
                tabla_pivot = df_group.set_index(eje_x_real)
            
            # 🔥 MEJORA DE EJES - MÁS NÍTIDOS
            fig_prof.update_xaxes(
                tickangle=-45 if len(df_group[eje_x_real].unique()) > 5 else 0,
                tickfont=dict(
                    size=14,  # 🔥 MÁS GRANDE
                    family='Arial Black',  # 🔥 NEGRITA
                    color='black',  # 🔥 NEGRO (mejor contraste)
                    weight='bold'  # 🔥 NEGRITA
                ),
                title_font=dict(
                    size=16,
                    family='Arial Black',
                    color='black',
                    weight='bold'
                ),
                gridcolor='lightgray',
                linecolor='black',
                linewidth=2
            )
            
            fig_prof.update_yaxes(
                tickfont=dict(
                    size=14,
                    family='Arial Black',
                    color='black',
                    weight='bold'
                ),
                title_font=dict(
                    size=16,
                    family='Arial Black',
                    color='black',
                    weight='bold'
                ),
                gridcolor='lightgray',
                linecolor='black',
                linewidth=2,
                tickformat=',.0f'
            )
            
            # Mejoras de diseño profesional
            fig_prof.update_layout(
                xaxis_title=eje_x_real.title(),
                yaxis_title=titulo_metrica,
                plot_bgcolor='white',  # 🔥 FONDO BLANCO
                paper_bgcolor='white',  # 🔥 FONDO BLANCO
                font=dict(
                    family='Arial Black', 
                    size=16, 
                    color='black',  # 🔥 TEXTO NEGRO
                    weight='bold'
                ),
                title_font=dict(
                    size=20,
                    family='Arial Black',
                    color='#003366',
                    weight='bold'
                ),
                legend=dict(
                    title=dict(
                        text=agrupar_real.title() if agrupar_real != "NINGUNO" else "",
                        font=dict(size=14, family='Arial Black', color='black', weight='bold')
                    ),
                    font=dict(size=12, family='Arial', color='black'),
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                ),
                height=600,
                margin=dict(l=80, r=60, t=120, b=100),
                hovermode='x unified'
            )
            
            # Mostrar gráfico
            st.plotly_chart(fig_prof, use_container_width=True, key="prof_grafico_general")
            
            # TABLA PROFESIONAL
            st.markdown("#### 📋 TABLA COMPARATIVA DETALLADA")
            
            # 🔥 MEJORA 3: Formato con comas de millares
            tabla_formateada = tabla_pivot.copy()
            for col in tabla_formateada.columns:
                if metrica == "💰 Ventas Totales" or metrica == "🎯 Ticket Promedio":
                    tabla_formateada[col] = tabla_formateada[col].apply(lambda x: f"S/ {x:,.2f}")
                else:
                    tabla_formateada[col] = tabla_formateada[col].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(
                tabla_formateada,
                use_container_width=True,
                height=400
            )
            
            # Exportar
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                csv_tabla = tabla_pivot.to_csv().encode('utf-8')
                st.download_button(
                    label="📥 DESCARGAR TABLA (CSV)",
                    data=csv_tabla,
                    file_name=f"comparacion_{eje_x_real}_vs_{agrupar_real}.csv",
                    mime="text/csv",
                    key="btn_prof_csv",
                    use_container_width=True
                )
            
            with col_exp2:
                # Versión Excel simple
                output_prof = io.BytesIO()
                with pd.ExcelWriter(output_prof, engine='openpyxl') as writer:
                    tabla_pivot.to_excel(writer, sheet_name='Comparacion')
                st.download_button(
                    label="📥 DESCARGAR TABLA (EXCEL)",
                    data=output_prof.getvalue(),
                    file_name=f"comparacion_{eje_x_real}_vs_{agrupar_real}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="btn_prof_excel",
                    use_container_width=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==============================================
    # PESTAÑA 2: COMPARADOR POR DISTRITOS (MEJORADO)
    # ==============================================
    with tab_comp2:
        st.markdown('<div class="comparador-card">', unsafe_allow_html=True)
        st.markdown("### 🏙️ COMPARADOR PROFESIONAL DE DISTRITOS")
        
        st.markdown("""
        <p style='color:#666; font-size:14px; margin-bottom:20px;'>
        Análisis detallado del desempeño por distritos con indicadores clave y visualizaciones profesionales.
        </p>
        """, unsafe_allow_html=True)
        
        # Filtros específicos para distritos
        col_dist1, col_dist2, col_dist3 = st.columns(3)
        
        with col_dist1:
            años_dist = st.multiselect(
                "📆 Años a comparar",
                options=[2023, 2024, 2025, 2026],
                default=[2025, 2026],
                key="dist_años"
            )
        
        with col_dist2:
            provincias_dist = sorted(df_base[df_base['AÑO'].isin(años_dist)]['PROVINCIA'].unique())
            provincia_sel = st.selectbox(
                "📍 Seleccionar Provincia (opcional)",
                options=["TODAS LAS PROVINCIAS"] + list(provincias_dist),
                key="dist_provincia"
            )
        
        with col_dist3:
            top_n = st.slider(
                "🎯 Top N distritos",
                min_value=5,
                max_value=30,
                value=15,
                step=5,
                key="dist_top"
            )
        
        # Filtrar datos para distritos
        df_dist = df_base[df_base['AÑO'].isin(años_dist)].copy()
        
        if provincia_sel != "TODAS LAS PROVINCIAS":
            df_dist = df_dist[df_dist['PROVINCIA'] == provincia_sel]
        
        # Análisis por distrito
        if not df_dist.empty:
            # Resumen por distrito
            distritos_resumen = df_dist.groupby(['PROVINCIA', 'DISTRITO']).agg({
                'TOTAL': ['sum', 'mean', 'count'],
                'CLIENTE': 'nunique'
            }).round(2)
            
            distritos_resumen.columns = ['VENTAS_TOTALES', 'TICKET_PROMEDIO', 'OPERACIONES', 'CLIENTES_UNICOS']
            distritos_resumen = distritos_resumen.reset_index()
            distritos_resumen = distritos_resumen.sort_values('VENTAS_TOTALES', ascending=False).head(top_n)
            
            # 🔥 MEJORA 4: Métricas con comas de millares
            st.markdown("#### 📊 MÉTRICAS GLOBALES DE DISTRITOS")
            col_md1, col_md2, col_md3, col_md4 = st.columns(4)
            
            with col_md1:
                st.metric(
                    "🏙️ Distritos Atendidos",
                    f"{len(distritos_resumen):,}",
                    help="Número de distritos en el top"
                )
            
            with col_md2:
                st.metric(
                    "💰 Ventas Totales",
                    f"S/ {distritos_resumen['VENTAS_TOTALES'].sum():,.0f}",
                    help="Suma de ventas de todos los distritos"
                )
            
            with col_md3:
                st.metric(
                    "📦 Total Operaciones",
                    f"{distritos_resumen['OPERACIONES'].sum():,.0f}",
                    help="Total de operaciones"
                )
            
            with col_md4:
                st.metric(
                    "👥 Clientes Atendidos",
                    f"{distritos_resumen['CLIENTES_UNICOS'].sum():,.0f}",
                    help="Total de clientes únicos"
                )
            
            # GRÁFICO 1: Top Distritos por Ventas
            # GRÁFICO 1: Top Distritos por Ventas - VERSIÓN MEJORADA
            st.markdown("#### 🏆 TOP DISTRITOS POR VENTAS")
            
            fig_dist1 = px.bar(
                distritos_resumen.head(10),
                x='VENTAS_TOTALES',
                y='DISTRITO',
                orientation='h',
                title=f"<b>Top 10 Distritos por Ventas Totales</b>",
                labels={'VENTAS_TOTALES': 'Ventas Totales (S/)', 'DISTRITO': 'Distrito'},
                text=distritos_resumen.head(10)['VENTAS_TOTALES'].apply(lambda x: f"S/ {x:,.0f}"),
                color='VENTAS_TOTALES',
                color_continuous_scale='Blues',
                template='plotly_white'
            )
            
            fig_dist1.update_traces(
                textposition='inside',
                textfont=dict(
                    size=13, 
                    family='Arial Black', 
                    color='white',
                    weight='bold'
                ),
                marker_line_width=1.5,
                marker_line_color='black'
            )
            
            # 🔥 EJES MÁS NÍTIDOS
            fig_dist1.update_xaxes(
                tickfont=dict(
                    size=13,
                    family='Arial Black',
                    color='black',
                    weight='bold'
                ),
                title_font=dict(
                    size=15,
                    family='Arial Black',
                    color='black',
                    weight='bold'
                ),
                gridcolor='lightgray',
                linecolor='black',
                linewidth=2,
                tickformat=',.0f'
            )
            
            fig_dist1.update_yaxes(
                tickfont=dict(
                    size=13,
                    family='Arial Black',
                    color='black',
                    weight='bold'
                ),
                title_font=dict(
                    size=15,
                    family='Arial Black',
                    color='black',
                    weight='bold'
                ),
                gridcolor='lightgray',
                linecolor='black',
                linewidth=2
            )
            
            fig_dist1.update_layout(
                height=550,
                xaxis_title="Ventas Totales (S/)",
                yaxis_title="",
                plot_bgcolor='white',  # 🔥 FONDO BLANCO
                paper_bgcolor='white',  # 🔥 FONDO BLANCO
                font=dict(
                    family='Arial Black', 
                    size=14, 
                    color='black',
                    weight='bold'
                ),
                title_font=dict(
                    size=18,
                    family='Arial Black',
                    color='#003366',
                    weight='bold'
                ),
                coloraxis_showscale=False,
                margin=dict(l=180, r=30, t=60, b=60)
            )
            
            st.plotly_chart(fig_dist1, use_container_width=True, key="fig_distritos_ventas")
            
            # GRÁFICO 2: Comparativo Ticket Promedio vs Operaciones
            # GRÁFICO 2: Comparativo Ticket Promedio vs Operaciones - VERSIÓN MEJORADA
            st.markdown("#### 📈 ANÁLISIS DE RENDIMIENTO POR DISTRITO")
            
            fig_dist2 = px.scatter(
                distritos_resumen,
                x='OPERACIONES',
                y='TICKET_PROMEDIO',
                size='VENTAS_TOTALES',
                color='PROVINCIA',
                hover_name='DISTRITO',
                title="<b>Matriz de Rendimiento: Operaciones vs Ticket Promedio</b>",
                labels={
                    'OPERACIONES': 'Número de Operaciones',
                    'TICKET_PROMEDIO': 'Ticket Promedio (S/)',
                    'VENTAS_TOTALES': 'Ventas Totales'
                },
                template='plotly_white',
                size_max=50
            )
            
            fig_dist2.update_traces(
                marker=dict(
                    line=dict(width=2, color='black')
                )
            )
            
            # 🔥 EJES MÁS NÍTIDOS
            fig_dist2.update_xaxes(
                tickfont=dict(
                    size=13,
                    family='Arial Black',
                    color='black',
                    weight='bold'
                ),
                title_font=dict(
                    size=15,
                    family='Arial Black',
                    color='black',
                    weight='bold'
                ),
                gridcolor='lightgray',
                linecolor='black',
                linewidth=2,
                tickformat=',.0f'
            )
            
            fig_dist2.update_yaxes(
                tickfont=dict(
                    size=13,
                    family='Arial Black',
                    color='black',
                    weight='bold'
                ),
                title_font=dict(
                    size=15,
                    family='Arial Black',
                    color='black',
                    weight='bold'
                ),
                gridcolor='lightgray',
                linecolor='black',
                linewidth=2,
                tickprefix='S/ ',
                tickformat=',.0f'
            )
            
            fig_dist2.update_layout(
                height=550,
                plot_bgcolor='white',  # 🔥 FONDO BLANCO
                paper_bgcolor='white',  # 🔥 FONDO BLANCO
                font=dict(
                    family='Arial', 
                    size=13, 
                    color='black'
                ),
                title_font=dict(
                    size=18,
                    family='Arial Black',
                    color='#003366',
                    weight='bold'
                ),
                legend=dict(
                    font=dict(size=12, family='Arial', color='black'),
                    title=dict(
                        text="Provincia",
                        font=dict(size=13, family='Arial Black', color='black', weight='bold')
                    )
                ),
                margin=dict(l=80, r=50, t=80, b=60)
            )
            
            st.plotly_chart(fig_dist2, use_container_width=True, key="fig_distritos_scatter")

        # GRÁFICO 3: Heatmap de Distritos por Año (si hay múltiples años)
            if len(años_dist) > 1:
                st.markdown("#### 🔥 HEATMAP: Evolución de Ventas por Distrito")
                
                # Preparar datos para heatmap
                distritos_heat = df_dist[df_dist['DISTRITO'].isin(distritos_resumen['DISTRITO'].head(15))]
                heat_data = distritos_heat.groupby(['DISTRITO', 'AÑO'])['TOTAL'].sum().reset_index()
                
                # Convertir años a string para evitar decimales
                heat_data['AÑO'] = heat_data['AÑO'].astype(int).astype(str)
                heat_pivot = heat_data.pivot(index='DISTRITO', columns='AÑO', values='TOTAL').fillna(0)
                
                fig_heat = px.imshow(
                    heat_pivot,
                    text_auto='.0f',
                    aspect="auto",
                    color_continuous_scale='Viridis',
                    title="<b>Evolución de Ventas por Distrito</b>",
                    labels=dict(x="Año", y="Distrito", color="Ventas (S/)")
                )
                
                # 🔥 MEJORA: Texto más nítido en heatmap
                fig_heat.update_traces(
                    texttemplate='%{z:,.0f}',
                    textfont=dict(
                        size=11,
                        family='Arial Black',
                        color='black',
                        weight='bold'
                    )
                )
                
                fig_heat.update_xaxes(
                    tickfont=dict(
                        size=13,
                        family='Arial Black',
                        color='black',
                        weight='bold'
                    ),
                    title_font=dict(
                        size=15,
                        family='Arial Black',
                        color='black',
                        weight='bold'
                    )
                )
                
                fig_heat.update_yaxes(
                    tickfont=dict(
                        size=12,
                        family='Arial Black',
                        color='black',
                        weight='bold'
                    ),
                    title_font=dict(
                        size=15,
                        family='Arial Black',
                        color='black',
                        weight='bold'
                    )
                )
                
                fig_heat.update_layout(
                    height=550,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family='Arial', size=13, color='black'),
                    title_font=dict(
                        size=18,
                        family='Arial Black',
                        color='#003366',
                        weight='bold'
                    ),
                    coloraxis_colorbar=dict(
                        title=dict(
                            text="Ventas (S/)",
                            font=dict(size=13, family='Arial Black', color='black', weight='bold')
                        ),
                        tickfont=dict(size=12, family='Arial', color='black'),
                        tickformat=',.0f'
                    ),
                    margin=dict(l=120, r=30, t=80, b=60)
                )
                
                st.plotly_chart(fig_heat, use_container_width=True, key="fig_distritos_heat")
            
            # 🔥 MEJORA 7: TABLA DETALLADA CON COMAS DE MILLARES
            st.markdown("#### 📋 TABLA DETALLADA DE DISTRITOS")
            
            # Formatear tabla con comas
            distritos_show = distritos_resumen.copy()
            distritos_show['VENTAS_TOTALES'] = distritos_show['VENTAS_TOTALES'].apply(lambda x: f"S/ {x:,.2f}")
            distritos_show['TICKET_PROMEDIO'] = distritos_show['TICKET_PROMEDIO'].apply(lambda x: f"S/ {x:,.2f}")
            distritos_show['OPERACIONES'] = distritos_show['OPERACIONES'].apply(lambda x: f"{x:,.0f}")
            distritos_show['CLIENTES_UNICOS'] = distritos_show['CLIENTES_UNICOS'].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(
                distritos_show,
                use_container_width=True,
                height=400,
                column_config={
                    "PROVINCIA": "Provincia",
                    "DISTRITO": "Distrito",
                    "VENTAS_TOTALES": "Ventas Totales",
                    "TICKET_PROMEDIO": "Ticket Promedio",
                    "OPERACIONES": "Operaciones",
                    "CLIENTES_UNICOS": "Clientes Únicos"
                }
            )
            
            # Exportar datos de distritos
            col_exp_dist1, col_exp_dist2 = st.columns(2)
            
            with col_exp_dist1:
                # 🔥 MEJORA: Exportar con números sin formato
                distritos_export = distritos_resumen.copy()
                csv_dist = distritos_export.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 EXPORTAR ANÁLISIS DE DISTRITOS (CSV)",
                    data=csv_dist,
                    file_name=f"analisis_distritos_{'_'.join(map(str, años_dist))}.csv",
                    mime="text/csv",
                    key="btn_dist_csv",
                    use_container_width=True
                )
            
            with col_exp_dist2:
                # Detalle de clientes por distrito
                clientes_dist = df_dist[df_dist['DISTRITO'].isin(distritos_resumen['DISTRITO'])][['DISTRITO', 'CLIENTE', 'TOTAL']].copy()
                csv_clientes = clientes_dist.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 EXPORTAR CLIENTES POR DISTRITO (CSV)",
                    data=csv_clientes,
                    file_name=f"clientes_por_distrito.csv",
                    mime="text/csv",
                    key="btn_dist_clientes",
                    use_container_width=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==============================================
    # PESTAÑA 3: ANÁLISIS DE TENDENCIAS
    # ==============================================
    with tab_comp3:
        st.markdown('<div class="comparador-card">', unsafe_allow_html=True)
        st.markdown("### 📈 ANÁLISIS DE TENDENCIAS")
        st.markdown("Evolución temporal y proyecciones")
        
        # Aquí puedes agregar más análisis de tendencias si lo deseas
        st.info("🔧 Sección en desarrollo - Próximamente: análisis predictivo y proyecciones")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==============================================
    # PESTAÑA 4: DATOS DETALLADOS
    # ==============================================
    with tab_comp4:
        st.markdown('<div class="comparador-card">', unsafe_allow_html=True)
        st.markdown("### 📋 DATOS DETALLADOS")
        
        # Mostrar todos los registros filtrados
        if 'df_prof' in locals() and not df_prof.empty:
            df_detalle = df_prof[['FECHA', 'VENDEDOR', 'EMPRESA', 'CLIENTE', 'PROVINCIA', 'DISTRITO', 'TOTAL', 'AÑO', 'MES']].copy()
            df_detalle['TOTAL'] = df_detalle['TOTAL'].apply(lambda x: f"S/ {x:,.2f}")
            
            st.dataframe(
                df_detalle,
                use_container_width=True,
                height=500,
                column_config={
                    "FECHA": "Fecha",
                    "VENDEDOR": "Vendedor",
                    "EMPRESA": "Empresa",
                    "CLIENTE": "Cliente",
                    "PROVINCIA": "Provincia",
                    "DISTRITO": "Distrito",
                    "TOTAL": "Total",
                    "AÑO": "Año",
                    "MES": "Mes"
                }
            )
            
            # Exportar detalle
            csv_detalle = df_prof.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 EXPORTAR TODOS LOS REGISTROS (CSV)",
                data=csv_detalle,
                file_name="registros_detallados.csv",
                mime="text/csv",
                key="btn_detalle_csv",
                use_container_width=True
            )
        else:
            st.warning("⚠️ No hay datos para mostrar. Aplica filtros en la pestaña 'Comparador General' primero.")
        
        st.markdown('</div>', unsafe_allow_html=True)
   
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
