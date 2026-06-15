import streamlit as st
import pandas as pd
import sqlalchemy
import plotly.express as px
import urllib.parse
import queries

# 1. CONFIGURACIÓN DE LA PÁGINA
# Esto debe ser lo primero que se ejecuta en Streamlit
st.set_page_config(page_title="Plataforma de Seguridad Vial", page_icon="📊", layout="wide")

st.title("📊 Plataforma analítica de seguridad vial")
st.markdown("Herramienta interactiva para la exploración, visualización y análisis avanzado de siniestros vehiculares.")

# 2. CONEXIÓN A LA BASE DE DATOS
# st.cache_resource hace que la conexión se abra una sola vez y no cada vez que haces clic
@st.cache_resource
def iniciar_conexion():
    server = st.secrets["db_server"]
    database = st.secrets["db_name"]
    
    # Usar get() permite que las credenciales sean opcionales para usar Autenticación de Windows
    username = st.secrets.get("db_user", "")
    password = st.secrets.get("db_pass", "")
    
    # Permite especificar el driver desde secrets (por defecto ODBC Driver 17)
    # Esto es útil por si la PC de la universidad tiene otra versión instalada.
    driver = st.secrets.get("db_driver", "ODBC Driver 17 for SQL Server")
    driver = driver.replace(" ", "+") # Formato seguro para la URL

    if username and password:
        # Autenticación SQL Server
        password_encoded = urllib.parse.quote_plus(password)
        cadena_conexion = f"mssql+pyodbc://{username}:{password_encoded}@{server}/{database}?driver={driver}&TrustServerCertificate=yes&timeout=10"
    else:
        # Autenticación de Windows (Trusted_Connection=yes)
        cadena_conexion = f"mssql+pyodbc://@{server}/{database}?driver={driver}&Trusted_Connection=yes&TrustServerCertificate=yes&timeout=10"
        
    motor = sqlalchemy.create_engine(cadena_conexion)
    return motor

try:
    engine = iniciar_conexion()
    # Forzamos una conexión de prueba para validar credenciales inmediatamente
    with engine.connect() as conn:
        pass
    st.sidebar.success("✅ Conexión establecida")
except Exception as e:
    st.sidebar.error(f"❌ Error crítico de conexión: {e}")
    st.stop() # Detiene la app si no hay conexión

# --- FUNCIÓN CACHEADA PARA CONSULTAS ---
# Esto hace que tu app sea súper rápida y profesional. Si haces la misma consulta, 
# no vuelve a golpear la base de datos a menos que pase 1 hora (3600 segundos).
@st.cache_data(ttl=3600, show_spinner="Ejecutando consulta en la BD...")
def obtener_datos(query):
    return pd.read_sql(query, engine)

# 3. SELECTOR DE CONSULTAS EN LA BARRA LATERAL
st.sidebar.header("Navegación del Sistema")
opcion = st.sidebar.selectbox(
    "Seleccione un módulo:",
    ["1. Resumen Ejecutivo", 
     "2. Reportes Analíticos",
     "3. Entorno de Consultas Ad-Hoc",
     "4. Modelo Relacional (ERD)"]
)

st.divider()

# 4. LÓGICA DE LAS VISTAS
if opcion == "1. Resumen Ejecutivo":
    st.title("🏙️ Análisis de seguridad vial en Chicago")    
    st.markdown("---")
    
    col1, col2 = st.columns([1.6, 1])
    
    with col1:
        st.subheader("📌 Contexto del Proyecto")
        st.markdown("""
        <div style="text-align: justify;">
        La seguridad vial representa uno de los principales retos de salud y seguridad pública que enfrentan las grandes ciudades en Estados Unidos. <b>Chicago</b>, como tercera ciudad más poblada del país, concentra una densa red de vías urbanas con alto flujo de vehículos, peatones y ciclistas.
        <br><br>
        Según datos del Departamento de Transporte de Illinois (2024), la ciudad registra anualmente decenas de miles de siniestros viales. Los accidentes no se distribuyen de manera uniforme, sino que responden a factores como:
        <ul>
            <li>Estado de la infraestructura vial.</li>
            <li>Condiciones climáticas e Iluminación.</li>
            <li>Patrones de movilidad y comportamiento de los conductores.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div style="padding: 1rem; border-radius: 0.5rem; background-color: rgba(23, 114, 233, 0.1); border: 1px solid rgba(23, 114, 233, 0.2);">
            <p style="text-align: justify; margin-bottom: 0;">
            <b>🎯 Sobre la Base de Datos:</b><br><br>
            Registra accidentes ocurridos en vías públicas bajo la jurisdicción del Departamento de Policía local.<br><br>
            Vincula cada siniestro con su contexto físico, ambiental, causal y humano de manera holística, permitiendo identificar patrones temporales, espaciales y causales.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.subheader("🚀 Propósito del Análisis")
    st.markdown("""
    <p style="text-align: justify;">
    El propósito de esta plataforma es analizar los volúmenes de datos históricos para <b>apoyar la toma de decisiones estratégicas en materia de políticas públicas y seguridad urbana</b>, mediante la identificación de factores de riesgo, zonas de alta incidencia y patrones recurrentes.
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: rgba(39, 174, 96, 0.1); border: 1px solid rgba(39, 174, 96, 0.2); border-radius: 0.5rem; padding: 1rem;">
        <ul style="list-style: none; padding-left: 0; margin-bottom: 0;">
            <li style="display: flex; align-items: flex-start; margin-bottom: 0.5rem;">
                <span style="margin-right: 0.5rem;">✅</span>
                <span style="text-align: justify;"><b>Caracterizar</b> los incidentes según su contexto operativo.</span>
            </li>
            <li style="display: flex; align-items: flex-start; margin-bottom: 0.5rem;">
                <span style="margin-right: 0.5rem;">✅</span>
                <span style="text-align: justify;"><b>Geolocalizar</b> zonas de alta siniestralidad.</span>
            </li>
            <li style="display: flex; align-items: flex-start; margin-bottom: 0.5rem;">
                <span style="margin-right: 0.5rem;">✅</span>
                <span style="text-align: justify;"><b>Cuantificar el impacto humano</b> y material asociado a diversas variables.</span>
            </li>
            <li style="display: flex; align-items: flex-start; margin-bottom: 0.5rem;">
                <span style="margin-right: 0.5rem;">✅</span>
                <span style="text-align: justify;"><b>Identificar tendencias temporales</b> para la asignación eficiente de recursos.</span>
            </li>
            <li style="display: flex; align-items: flex-start; margin-bottom: 0;">
                <span style="margin-right: 0.5rem;">✅</span>
                <span style="text-align: justify;"><b>Evaluar causales principales</b> para la formulación de medidas preventivas.</span>
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("**Referencia:**  \nIllinois Department of Transportation. (2024). *Crash facts and statistics 2024*.")

elif opcion == "2. Reportes Analíticos":
    st.subheader("📊 Reportes de Inteligencia de Negocios (BI)")
    
    reporte_seleccionado = st.selectbox(
        "Seleccione el indicador a evaluar:",
        list(queries.REPORTES_ACADEMICOS.keys())
    )
    
    datos_reporte = queries.REPORTES_ACADEMICOS[reporte_seleccionado]
    query_sql = datos_reporte["sql"]
    
    with st.expander("🔍 Inspeccionar código SQL (Transact-SQL)"):
        st.code(query_sql, language="sql")
        
    try:
        with st.spinner("Ejecutando modelo analítico..."):
            df_reporte = obtener_datos(query_sql)
            
        if df_reporte.empty:
            st.warning("Ejecución completada. No se encontraron registros para los criterios establecidos.")
        else:
            st.success(f"✅ Extracción exitosa. {len(df_reporte)} registros obtenidos.")
            
            with st.expander("Visualizar matriz de datos", expanded=False):
                st.dataframe(df_reporte, use_container_width=True)
                csv = df_reporte.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Descargar resultados en CSV", data=csv, file_name='reporte.csv', mime='text/csv')
            
            st.divider()
            st.subheader("🎨 Configuración Visual")
            
            mapa_tipos = {"bar": "Barras", "line": "Líneas", "scatter": "Dispersión", "pie": "Pastel", "none": "Ninguno"}
            tipo_defecto = mapa_tipos.get(datos_reporte.get("chart", "none"), "Ninguno")
            
            col_controles, col_grafico = st.columns([1, 3])
            with col_controles:
                st.write("⚙️ **Opciones de Gráfico**")
                col_opciones = df_reporte.columns.tolist()
                
                opciones_graficas = ["Ninguno", "Barras", "Líneas", "Dispersión", "Pastel", "Mapa (Geolocalización)"]
                idx_tipo = opciones_graficas.index(tipo_defecto) if tipo_defecto in opciones_graficas else 0
                tipo_grafico = st.selectbox("Seleccione el tipo de visualización", opciones_graficas, index=idx_tipo)
                
                if tipo_grafico in ["Barras", "Líneas", "Dispersión", "Pastel"]:
                    idx_x = col_opciones.index(datos_reporte["x"]) if datos_reporte.get("x") in col_opciones else 0
                    eje_x = st.selectbox("Eje X (Categorías)", col_opciones, index=idx_x)
                    
                    idx_y = col_opciones.index(datos_reporte["y"]) if datos_reporte.get("y") in col_opciones else (len(col_opciones)-1 if len(col_opciones)>1 else 0)
                    eje_y = st.selectbox("Eje Y (Métricas)", col_opciones, index=idx_y)
                    
                elif tipo_grafico == "Mapa (Geolocalización)":
                    eje_lat = st.selectbox("Dimensión Latitud", col_opciones, index=0)
                    eje_lon = st.selectbox("Dimensión Longitud", col_opciones, index=min(1, len(col_opciones)-1))
            
            with col_grafico:
                if tipo_grafico != "Ninguno":
                    try:
                        if tipo_grafico == "Barras":
                            fig = px.bar(df_reporte, x=eje_x, y=eje_y, color=eje_x)
                        elif tipo_grafico == "Líneas":
                            fig = px.line(df_reporte, x=eje_x, y=eje_y, markers=True)
                        elif tipo_grafico == "Dispersión":
                            fig = px.scatter(df_reporte, x=eje_x, y=eje_y, color=eje_y, size=eje_y)
                        elif tipo_grafico == "Pastel":
                            fig = px.pie(df_reporte, names=eje_x, values=eje_y, hole=0.3)
                        elif tipo_grafico == "Mapa (Geolocalización)":
                            df_mapa = df_reporte.dropna(subset=[eje_lat, eje_lon])
                            fig = px.scatter_mapbox(df_mapa, lat=eje_lat, lon=eje_lon, zoom=10, mapbox_style="carto-positron")
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"❌ Error de renderizado visual. Verifique los tipos de datos en las columnas seleccionadas. Detalle: {e}")
                else:
                    st.info("👈 Utilice el panel lateral izquierdo para configurar la visualización deseada.")
    except Exception as e:
        st.error(f"❌ Error de base de datos: {e}")

elif opcion == "3. Entorno de Consultas Ad-Hoc":
    st.subheader("💻 Entorno de Exploración de Datos Ad-Hoc")
    st.write("Interfaz de ejecución de sentencias SQL personalizadas para análisis dinámico.")
    
    # Selector de consultas precargadas
    consulta_predefinida = st.selectbox(
        "💡 Seleccione una plantilla o elabore su propia sintaxis:",
        list(queries.CONSULTAS_INTERACTIVAS.keys())
    )
    texto_default = queries.CONSULTAS_INTERACTIVAS[consulta_predefinida]

    # Área de texto para que el usuario escriba su consulta
    query_usuario = st.text_area("Editor de Consultas (Transact-SQL):", value=texto_default, height=200)
    
    # Inicializar el estado de la sesión si no existe
    if 'df_custom' not in st.session_state:
        st.session_state['df_custom'] = None

    # Botón para ejecutar
    if st.button("🚀 Ejecutar Consulta"):
        if query_usuario.strip() != "":
            try:
                with st.spinner("Procesando consulta en el motor de base de datos..."):
                    # Usamos una ejecución manual con SQLAlchemy para manejar columnas duplicadas (ej: en SELECT * con JOIN)
                    with engine.connect() as conn:
                        resultado = conn.execute(sqlalchemy.text(query_usuario))
                        filas = resultado.fetchall()
                        
                        if filas:
                            # Extraemos los nombres de las columnas y renombramos los duplicados agregando un sufijo
                            columnas = resultado.keys()
                            columnas_limpias = []
                            vistos = {}
                            for col in columnas:
                                if col in vistos:
                                    vistos[col] += 1
                                    columnas_limpias.append(f"{col}_{vistos[col]}")
                                else:
                                    vistos[col] = 0
                                    columnas_limpias.append(col)
                                    
                            df_custom = pd.DataFrame(filas, columns=columnas_limpias)
                            st.session_state['df_custom'] = df_custom
                        else:
                            # Si la consulta se ejecutó pero no trajo resultados (ej. SELECT sin match)
                            st.session_state['df_custom'] = pd.DataFrame()
                
            except Exception as e:
                st.error(f"❌ Excepción en la ejecución de la consulta. Revise la sintaxis. Detalles: {e}")
                st.session_state['df_custom'] = None
        else:
            st.warning("⚠️ El área de texto está vacía. Ingrese una instrucción SQL válida.")
            
    # --- RENDERIZADO FUERA DEL BOTÓN (Para que sea interactivo) ---
    if st.session_state['df_custom'] is not None:
        df_custom = st.session_state['df_custom']
        
        if df_custom.empty:
            st.success("✅ Ejecución finalizada. La instrucción procesada no devolvió ningún conjunto de resultados.")
        else:
            st.success(f"✅ Datos cargados en memoria. Total de registros recuperados: {len(df_custom)}.")
            
            with st.expander("Visualizar matriz de datos", expanded=False):
                st.dataframe(df_custom, use_container_width=True)
                csv = df_custom.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Exportar Extracción (CSV)", data=csv, file_name='extraccion_ad_hoc.csv', mime='text/csv')
            
            st.divider()
            st.subheader("🎨 Generador Visual Dinámico")
            
            # Controles a la izquierda (1/4 del ancho) y Gráfico a la derecha (3/4 del ancho)
            col_controles, col_grafico = st.columns([1, 3])
            
            with col_controles:
                st.write("⚙️ **Opciones de Gráfico**")
                col_opciones = df_custom.columns.tolist()
                tipo_grafico = st.selectbox("Seleccione el tipo de visualización", ["Ninguno", "Barras", "Líneas", "Dispersión", "Pastel", "Mapa (Geolocalización)"])
                
                if tipo_grafico in ["Barras", "Líneas", "Dispersión", "Pastel"]:
                    eje_x = st.selectbox("Eje X (Categorías)", col_opciones, index=0)
                    eje_y = st.selectbox("Eje Y (Métricas)", col_opciones, index=len(col_opciones)-1 if len(col_opciones)>1 else 0)
                elif tipo_grafico == "Mapa (Geolocalización)":
                    eje_lat = st.selectbox("Dimensión Latitud", col_opciones, index=0)
                    eje_lon = st.selectbox("Dimensión Longitud", col_opciones, index=min(1, len(col_opciones)-1))
            
            with col_grafico:
                if tipo_grafico != "Ninguno":
                    try:
                        if tipo_grafico == "Barras":
                            fig_dinamica = px.bar(df_custom, x=eje_x, y=eje_y, color=eje_x)
                        elif tipo_grafico == "Líneas":
                            fig_dinamica = px.line(df_custom, x=eje_x, y=eje_y, markers=True)
                        elif tipo_grafico == "Dispersión":
                            fig_dinamica = px.scatter(df_custom, x=eje_x, y=eje_y, color=eje_y, size=eje_y)
                        elif tipo_grafico == "Pastel":
                            fig_dinamica = px.pie(df_custom, names=eje_x, values=eje_y, hole=0.3)
                        elif tipo_grafico == "Mapa (Geolocalización)":
                            df_mapa_custom = df_custom.dropna(subset=[eje_lat, eje_lon])
                            fig_dinamica = px.scatter_mapbox(df_mapa_custom, lat=eje_lat, lon=eje_lon, zoom=10, mapbox_style="carto-positron")
                        
                        st.plotly_chart(fig_dinamica, use_container_width=True)
                    except Exception as e:
                        st.error(f"❌ Error de renderizado visual. Verifique los tipos de datos en las columnas. Detalle: {e}")
                else:
                    st.info("👈 Utilice el panel lateral izquierdo para configurar la visualización deseada.")

elif opcion == "4. Modelo Relacional (ERD)":
    st.subheader("🕸️ Diagrama de Base de Datos")
    st.write("Representación estructurada generada automáticamente a partir de las restricciones de integridad referencial (Foreign Keys) del esquema actual.")
    
    try:
        with st.spinner("Mapeando topología de la base de datos..."):
            df_fks = obtener_datos(queries.QUERY_FKS)
            df_cols = obtener_datos(queries.QUERY_COLUMNS)
            
            # Construimos un string en formato DOT con tablas HTML
            dot_code = 'digraph ERD {\n'
            dot_code += 'rankdir=LR;\n'
            dot_code += 'node [shape=none, fontname="Helvetica", fontsize=10, margin=0];\n'
            dot_code += 'edge [fontname="Helvetica", fontsize=9, color="#555555", dir=forward];\n'
            
            tables = df_cols['TableName'].unique()
            for table in tables:
                table_data = df_cols[df_cols['TableName'] == table]
                
                # Definición de la tabla en formato HTML para Graphviz
                html = f'<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">'
                html += f'<tr><td bgcolor="#1772E9"><font color="white"><b>{table}</b></font></td></tr>'
                
                for _, row in table_data.iterrows():
                    col_name = row['ColumnName']
                    data_type = row['DataType']
                    is_pk = row['IsPrimaryKey'] == 1
                    
                    # Verifica si la columna es FK buscando en el dataframe de relaciones
                    is_fk = not df_fks[(df_fks['ParentTable'] == table) & (df_fks['ParentColumn'] == col_name)].empty
                    
                    key_str = " <b>[PK, FK]</b>" if (is_pk and is_fk) else (" <b>[PK]</b>" if is_pk else (" <i>[FK]</i>" if is_fk else ""))
                        
                    # El "port" permite conectar las flechas directamente a esta fila de la tabla
                    port_name = str(col_name).replace(" ", "_")
                    html += f'<tr><td align="left" port="{port_name}">{col_name}{key_str} <font color="#666666"><i>{data_type}</i></font></td></tr>'
                    
                html += '</table>>'
                dot_code += f'"{table}" [label={html}];\n'
                
            for _, row in df_fks.iterrows():
                parent_table = row["ParentTable"]
                parent_col = str(row["ParentColumn"]).replace(" ", "_")
                ref_table = row["RefTable"]
                ref_col = str(row["RefColumn"]).replace(" ", "_")
                
                # Crea la relación apuntando desde la columna FK directamente a la columna PK
                dot_code += f'"{parent_table}":"{parent_col}" -> "{ref_table}":"{ref_col}";\n'
                
            dot_code += '}'
            
            # Pasamos la cadena de texto directamente a la función nativa de Streamlit
            st.graphviz_chart(dot_code, use_container_width=True)
            
    except Exception as e:
        st.error(f"❌ Error al generar el diagrama: {e}")