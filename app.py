import streamlit as st
import pandas as pd
import sqlalchemy
import plotly.express as px
import urllib.parse
import queries

# 1. CONFIGURACIÓN DE LA PÁGINA
# Esto debe ser lo primero que se ejecuta en Streamlit
st.set_page_config(page_title="Crashes Dashboard", page_icon="🚗", layout="wide")

st.title(" Dashboard Analítico - Accidentes de Tránsito")
st.markdown("Bienvenido a mi portafolio de Ingeniería de Datos. Exploración interactiva de datos de colisiones vehiculares.")

# 2. CONEXIÓN A LA BASE DE DATOS
# st.cache_resource hace que la conexión se abra una sola vez y no cada vez que haces clic
@st.cache_resource
def iniciar_conexion():
    server = st.secrets["db_server"]
    database = st.secrets["db_name"]
    username = st.secrets["db_user"]
    password = st.secrets["db_pass"]
    
    # Permite especificar el driver desde secrets (por defecto ODBC Driver 17)
    # Esto es útil por si la PC de la universidad tiene otra versión instalada.
    driver = st.secrets.get("db_driver", "ODBC Driver 17 for SQL Server")
    driver = driver.replace(" ", "+") # Formato seguro para la URL

    # Codificamos la contraseña por si tiene caracteres especiales como @, #, etc.
    password_encoded = urllib.parse.quote_plus(password)
    
    # Agregamos timeout=10 para que no se quede colgado eternamente si la IP no responde
    cadena_conexion = f"mssql+pyodbc://{username}:{password_encoded}@{server}/{database}?driver={driver}&TrustServerCertificate=yes&timeout=10"
    motor = sqlalchemy.create_engine(cadena_conexion)
    return motor

try:
    engine = iniciar_conexion()
    # Forzamos una conexión de prueba para validar credenciales inmediatamente
    with engine.connect() as conn:
        pass
    st.sidebar.success("✅ Conectado a la Base de Datos")
except Exception as e:
    st.sidebar.error(f"❌ Error de conexión: {e}")
    st.stop() # Detiene la app si no hay conexión

# --- FUNCIÓN CACHEADA PARA CONSULTAS ---
# Esto hace que tu app sea súper rápida y profesional. Si haces la misma consulta, 
# no vuelve a golpear la base de datos a menos que pase 1 hora (3600 segundos).
@st.cache_data(ttl=3600, show_spinner="Ejecutando consulta en la BD...")
def obtener_datos(query):
    return pd.read_sql(query, engine)

# 3. SELECTOR DE CONSULTAS EN LA BARRA LATERAL
st.sidebar.header("Menú de Reportes")
opcion = st.sidebar.selectbox(
    "Selecciona el análisis:",
    ["1. Visión General", 
     "2. Reportes Predefinidos",
     "3. Consola SQL Libre",
     "4. Diagrama de Base de Datos (ERD)"]
)

st.divider()

# 4. LÓGICA DE LAS VISTAS
if opcion == "1. Visión General":
    st.title("🏙️ Análisis de Seguridad Vial en Chicago")
    st.markdown("---")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.subheader("📌 Contexto del Proyecto")
        st.markdown("""
        La seguridad vial representa uno de los principales retos de salud y seguridad pública que enfrentan las grandes ciudades en Estados Unidos. **Chicago**, como tercera ciudad más poblada del país, concentra una densa red de vías urbanas con alto flujo de vehículos, peatones y ciclistas.
        
        Según datos del Departamento de Transporte de Illinois (2024), la ciudad registra anualmente decenas de miles de siniestros viales. Los accidentes no se distribuyen de manera uniforme, sino que responden a factores como:
        * Estado de la infraestructura vial.
        * Condiciones climáticas e Iluminación.
        * Patrones de movilidad y comportamiento de los conductores.
        """)
        
    with col2:
        st.info("""
        **🎯 Sobre la Base de Datos:**
        Registra accidentes ocurridos en vías públicas bajo la jurisdicción del Departamento de Policía local.
        
        Vincula cada siniestro con su contexto físico, ambiental, causal y humano de manera holística, permitiendo identificar patrones temporales, espaciales y causales.
        """)
        
    st.markdown("---")
    st.subheader("🚀 Propósito del Análisis")
    st.markdown("""
    El propósito del presente informe es analizar la base de datos con el fin de **apoyar a la toma de decisiones en materia de seguridad vial pública**, mediante la identificación de factores de riesgo y patrones recurrentes.
    """)
    st.success("✅ **Caracterizar** los accidentes según sus condiciones de ocurrencia.\n\n✅ **Geolocalizar** zonas críticas con base en el nivel de incidencia.\n\n✅ **Analizar el impacto humano** de los accidentes en relación a sus condiciones.\n\n✅ **Identificar patrones temporales** para orientar operativos preventivos.\n\n✅ **Determinar las causas** más frecuentes y peligrosas.")

elif opcion == "2. Reportes Predefinidos":
    st.subheader("📊 Reportes Analíticos")
    
    reporte_seleccionado = st.selectbox(
        "Selecciona el reporte a visualizar:",
        list(queries.REPORTES_ACADEMICOS.keys())
    )
    
    datos_reporte = queries.REPORTES_ACADEMICOS[reporte_seleccionado]
    query_sql = datos_reporte["sql"]
    
    with st.expander("🔍 Ver código SQL utilizado"):
        st.code(query_sql, language="sql")
        
    try:
        with st.spinner("Ejecutando modelo analítico..."):
            df_reporte = obtener_datos(query_sql)
            
        if df_reporte.empty:
            st.warning("La consulta se ejecutó correctamente, pero no devolvió ninguna fila.")
        else:
            st.success(f"✅ Consulta exitosa. Se recuperaron {len(df_reporte)} registros.")
            
            with st.expander("Ver tabla de resultados", expanded=False):
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
                
                opciones_graficas = ["Ninguno", "Barras", "Líneas", "Dispersión", "Pastel"]
                idx_tipo = opciones_graficas.index(tipo_defecto) if tipo_defecto in opciones_graficas else 0
                tipo_grafico = st.selectbox("Tipo de gráfico", opciones_graficas, index=idx_tipo)
                
                if tipo_grafico != "Ninguno":
                    idx_x = col_opciones.index(datos_reporte["x"]) if datos_reporte.get("x") in col_opciones else 0
                    eje_x = st.selectbox("Eje X (o Nombres)", col_opciones, index=idx_x)
                    
                    idx_y = col_opciones.index(datos_reporte["y"]) if datos_reporte.get("y") in col_opciones else (len(col_opciones)-1 if len(col_opciones)>1 else 0)
                    eje_y = st.selectbox("Eje Y (o Valores)", col_opciones, index=idx_y)
            
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
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"❌ No se pudo generar el gráfico con estas columnas. Intenta cambiar los ejes. Detalle: {e}")
                else:
                    st.info("👈 Selecciona un tipo de gráfico en el menú izquierdo para visualizar los datos.")
    except Exception as e:
        st.error(f"❌ Error de base de datos: {e}")

elif opcion == "3. Consola SQL Libre":
    st.subheader("💻 Consola SQL Libre")
    st.write("Escribe tu propia consulta SQL para explorar la base de datos en tiempo real.")
    
    # Selector de consultas precargadas
    consulta_predefinida = st.selectbox(
        "💡 Selecciona una consulta de ejemplo o escribe la tuya:",
        list(queries.CONSULTAS_INTERACTIVAS.keys())
    )
    texto_default = queries.CONSULTAS_INTERACTIVAS[consulta_predefinida]

    # Área de texto para que el usuario escriba su consulta
    query_usuario = st.text_area("Ingresa tu consulta SQL aquí (Soporta comentarios):", value=texto_default, height=200)
    
    # Inicializar el estado de la sesión si no existe
    if 'df_custom' not in st.session_state:
        st.session_state['df_custom'] = None

    # Botón para ejecutar
    if st.button("🚀 Ejecutar Consulta"):
        if query_usuario.strip() != "":
            try:
                with st.spinner("Ejecutando tu consulta en el servidor..."):
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
                st.error(f"❌ Error de sintaxis o de base de datos: {e}")
                st.session_state['df_custom'] = None
        else:
            st.warning("⚠️ Por favor, escribe una consulta SQL antes de presionar el botón.")
            
    # --- RENDERIZADO FUERA DEL BOTÓN (Para que sea interactivo) ---
    if st.session_state['df_custom'] is not None:
        df_custom = st.session_state['df_custom']
        
        if df_custom.empty:
            st.success("✅ La consulta se ejecutó correctamente (ej. contenía solo comentarios o no retornaba filas).")
        else:
            st.success(f"✅ Consulta en memoria. Se recuperaron {len(df_custom)} filas.")
            
            with st.expander("Ver tabla de resultados", expanded=False):
                st.dataframe(df_custom, use_container_width=True)
                csv = df_custom.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Descargar resultados en CSV", data=csv, file_name='query_libre.csv', mime='text/csv')
            
            st.divider()
            st.subheader("🎨 Generador de Gráficos Libre")
            
            # Controles a la izquierda (1/4 del ancho) y Gráfico a la derecha (3/4 del ancho)
            col_controles, col_grafico = st.columns([1, 3])
            
            with col_controles:
                st.write("⚙️ **Opciones de Gráfico**")
                col_opciones = df_custom.columns.tolist()
                tipo_grafico = st.selectbox("Tipo de gráfico", ["Ninguno", "Barras", "Líneas", "Dispersión", "Pastel"])
                
                if tipo_grafico != "Ninguno":
                    eje_x = st.selectbox("Eje X (o Nombres)", col_opciones, index=0)
                    eje_y = st.selectbox("Eje Y (o Valores)", col_opciones, index=len(col_opciones)-1 if len(col_opciones)>1 else 0)
            
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
                        
                        st.plotly_chart(fig_dinamica, use_container_width=True)
                    except Exception as e:
                        st.error(f"❌ No se pudo generar el gráfico con estas columnas. Intenta cambiar los ejes. Detalle: {e}")
                else:
                    st.info("👈 Selecciona un tipo de gráfico en el menú izquierdo para visualizar los datos.")

elif opcion == "4. Diagrama de Base de Datos (ERD)":
    st.subheader("🕸️ Diagrama de Base de Datos (ERD)")
    st.write("Este diagrama se genera automáticamente leyendo las relaciones (Llaves Foráneas) de la base de datos conectada.")
    
    try:
        with st.spinner("Generando diagrama relacional..."):
            df_fks = obtener_datos(queries.QUERY_FKS)
            df_tables = obtener_datos(queries.QUERY_TABLES)
            
            # Construimos un string en formato DOT para que Streamlit grafique
            dot_code = 'digraph ERD {\n'
            dot_code += 'rankdir=LR;\n'
            dot_code += 'node [shape=box, style=filled, color=lightblue, fontname="Arial"];\n'
            
            for index, row in df_tables.iterrows():
                dot_code += f'"{row["TableName"]}";\n'
                
            for index, row in df_fks.iterrows():
                dot_code += f'"{row["ParentTable"]}" -> "{row["RefTable"]}" [label="{row["ParentColumn"]} -> {row["RefColumn"]}", fontsize=9];\n'
                
            dot_code += '}'
            
            # Pasamos la cadena de texto directamente a la función nativa de Streamlit
            st.graphviz_chart(dot_code, use_container_width=True)
            
    except Exception as e:
        st.error(f"❌ Error al generar el diagrama: {e}")