import streamlit as st
import pandas as pd
import sqlalchemy
import plotly.express as px
import urllib.parse

# 1. CONFIGURACIÓN DE LA PÁGINA
# Esto debe ser lo primero que se ejecuta en Streamlit
st.set_page_config(page_title="Dashboard Northwind", page_icon="📊", layout="wide")

st.title("📊 Dashboard Universitario - Base de Datos Northwind")
st.markdown("Bienvenido a mi portafolio de Ingeniería de Datos. Aquí visualizamos consultas SQL complejas ejecutadas en tiempo real.")

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
     "2. Facturación por Categoría (JOIN de 5 tablas)", 
     "3. Rendimiento de Empleados (Window Functions)",
     "4. Consola SQL Interactiva"]
)

st.divider()

# 4. LÓGICA DE LAS VISTAS
if opcion == "1. Visión General":
    st.subheader("👋 Visión General del Proyecto")
    st.write("Usa el menú de la izquierda para navegar entre los diferentes reportes SQL generados dinámicamente.")
    
elif opcion == "2. Facturación por Categoría (JOIN de 5 tablas)":
    st.subheader("📦 Ventas Totales por Categoría de Producto")
    st.write("Esta consulta encadena `Customers`, `Orders`, `Order Details`, `Products` y `Categories`.")
    
    # Esta es tu consulta extraída del PDF ID9_1 (JOINs Encadenados)
    query_facturacion = """
        SELECT 
            CAT.CategoryName AS Categoria, 
            SUM(OD.Quantity * OD.UnitPrice) AS Ingreso_Total
        FROM Customers AS C
        JOIN Orders AS O ON O.CustomerID = C.CustomerID
        JOIN [Order Details] AS OD ON OD.OrderID = O.OrderID
        JOIN Products AS P ON P.ProductID = OD.ProductID
        JOIN Categories AS CAT ON CAT.CategoryID = P.CategoryID
        GROUP BY CAT.CategoryName
        ORDER BY Ingreso_Total DESC;
    """
    
    # Ejecutamos la consulta y la guardamos en un DataFrame de Pandas
    try:
        df_cat = obtener_datos(query_facturacion)
        
        if df_cat.empty:
            st.warning("La consulta se ejecutó, pero no devolvió datos.")
            st.stop()

        col1, col2 = st.columns([1, 2]) # El gráfico será el doble de ancho que la tabla
        
        with col1:
            st.dataframe(df_cat, use_container_width=True)
            
        with col2:
            # Gráfico de barras interactivo con Plotly
            fig = px.bar(df_cat, x='Categoria', y='Ingreso_Total', 
                         title="Ingresos por Categoría",
                         color='Ingreso_Total', 
                         color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Error al ejecutar la consulta SQL: {e}")

elif opcion == "3. Rendimiento de Empleados (Window Functions)":
    st.subheader("🏆 Aporte de Empleados al Total del País")
    
    # Esta es una adaptación de tu PDF de Window Functions
    query_empleados = """
        WITH VentasBase AS (
            SELECT 
                E.FirstName + ' ' + E.LastName AS Empleado, 
                E.Country AS Pais,
                SUM(OD.Quantity * OD.UnitPrice * (1 - OD.Discount)) AS TotalEmpleado 
            FROM Employees AS E 
            JOIN Orders AS O ON O.EmployeeID = E.EmployeeID 
            JOIN [Order Details] AS OD ON OD.OrderID = O.OrderID 
            GROUP BY E.EmployeeID, E.FirstName, E.LastName, E.Country
        )
        SELECT 
            Empleado, 
            Pais, 
            TotalEmpleado,
            SUM(TotalEmpleado) OVER(PARTITION BY Pais) AS TotalPais
        FROM VentasBase
        ORDER BY Pais, TotalEmpleado DESC;
    """
    
    try:
        df_emp = obtener_datos(query_empleados)
        
        if df_emp.empty:
            st.warning("La consulta se ejecutó, pero no devolvió datos.")
            st.stop()

        # Creamos un gráfico de 'Sunburst' (Dona jerárquica) para ver País -> Empleado
        fig2 = px.sunburst(df_emp, path=['Pais', 'Empleado'], values='TotalEmpleado',
                           title="Distribución de Ventas: País vs Empleado")
        
        st.plotly_chart(fig2, use_container_width=True)
        
        with st.expander("Ver tabla de datos (Window Functions aplicadas)"):
            st.dataframe(df_emp, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Error al ejecutar la consulta SQL: {e}")

elif opcion == "4. Consola SQL Interactiva":
    st.subheader("💻 Consola SQL Interactiva")
    st.write("Escribe tu propia consulta SQL para explorar la base de datos en tiempo real.")
    
    # Área de texto para que el usuario escriba su consulta
    query_usuario = st.text_area("Ingresa tu consulta SQL aquí (Ej: SELECT TOP 10 * FROM Customers):", height=200)
    
    # Botón para ejecutar
    if st.button("🚀 Ejecutar Consulta"):
        if query_usuario.strip() != "":
            try:
                with st.spinner("Ejecutando tu consulta en el servidor..."):
                    # Usamos pd.read_sql directamente (sin caché) para que siempre refleje lo que acabas de escribir
                    df_custom = pd.read_sql(query_usuario, engine)
                
                if df_custom.empty:
                    st.warning("La consulta se ejecutó correctamente, pero no devolvió ninguna fila.")
                else:
                    st.success(f"✅ Consulta ejecutada con éxito. Se recuperaron {len(df_custom)} filas.")
                    st.dataframe(df_custom, use_container_width=True)
                    
                    # Plus profesional: Botón de descarga de los resultados
                    csv = df_custom.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Descargar resultados en CSV",
                        data=csv,
                        file_name='resultados_personalizados.csv',
                        mime='text/csv',
                    )
            except Exception as e:
                st.error(f"❌ Error de sintaxis o de base de datos: {e}")
        else:
            st.warning("⚠️ Por favor, escribe una consulta SQL antes de presionar el botón.")