# Consultas de análisis principal
QUERY_CLIMA = """
    SELECT 
        W.WEATHER_CONDITION AS Clima, 
        COUNT(C.CRASH_RECORD_ID) AS Total_Accidentes
    FROM CRASH AS C
    JOIN WEATHER AS W ON C.WEATHER_ID = W.WEATHER_ID
    GROUP BY W.WEATHER_CONDITION
    ORDER BY Total_Accidentes DESC;
"""

QUERY_LESIONES = """
    SELECT 
        MOST_SEVERE_INJURY AS Severidad,
        SUM(INJURIES_TOTAL) AS Total_Lesionados,
        SUM(INJURIES_FATAL) AS Total_Muertes
    FROM INJURIES
    GROUP BY MOST_SEVERE_INJURY
    ORDER BY Total_Lesionados DESC;
"""

# Consultas del sistema (Esquema/Diagrama)
QUERY_FKS = """
    SELECT 
        tp.name AS ParentTable,
        cp.name AS ParentColumn,
        tr.name AS RefTable,
        cr.name AS RefColumn
    FROM sys.foreign_keys fk
    INNER JOIN sys.tables tp ON fk.parent_object_id = tp.object_id
    INNER JOIN sys.tables tr ON fk.referenced_object_id = tr.object_id
    INNER JOIN sys.foreign_key_columns fkc ON fkc.constraint_object_id = fk.object_id
    INNER JOIN sys.columns cp ON fkc.parent_column_id = cp.column_id AND fkc.parent_object_id = cp.object_id
    INNER JOIN sys.columns cr ON fkc.referenced_column_id = cr.column_id AND fkc.referenced_object_id = cr.object_id
"""

QUERY_COLUMNS = """
    SELECT 
        c.TABLE_NAME AS TableName,
        c.COLUMN_NAME AS ColumnName,
        c.DATA_TYPE AS DataType,
        CASE WHEN pk.COLUMN_NAME IS NOT NULL THEN 1 ELSE 0 END AS IsPrimaryKey
    FROM INFORMATION_SCHEMA.COLUMNS c
    INNER JOIN sys.tables t ON c.TABLE_NAME = t.name
    LEFT JOIN (
        SELECT ku.TABLE_NAME, ku.COLUMN_NAME
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS tc
        INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS ku
            ON tc.CONSTRAINT_TYPE = 'PRIMARY KEY' 
            AND tc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
    ) pk ON c.TABLE_NAME = pk.TABLE_NAME AND c.COLUMN_NAME = pk.COLUMN_NAME
    ORDER BY c.TABLE_NAME, c.ORDINAL_POSITION;
"""

# Consultas interactivas predefinidas para la consola
CONSULTAS_INTERACTIVAS = {
    "--- Escribe tu propia consulta ---": "",
    "🚗 Daños vs Promedio de Unidades Involucradas": "-- Agrupación básica evaluando el daño\nSELECT \n    DAMAGE AS Nivel_Dano,\n    AVG(CAST(NUM_UNITS AS FLOAT)) AS Promedio_Vehiculos_Involucrados\nFROM CRASH\nGROUP BY DAMAGE\nORDER BY Promedio_Vehiculos_Involucrados DESC;",
    "🛣️ Top 10 Calles con más accidentes": "-- JOIN para ver la calle con más incidencias\nSELECT TOP 10\n    L.STREET_NAME,\n    COUNT(C.CRASH_RECORD_ID) AS Total_Accidentes\nFROM CRASH C\nJOIN LOCATION L ON C.LOCATION_ID = L.LOCATION_ID\nGROUP BY L.STREET_NAME\nORDER BY Total_Accidentes DESC;",
    "🏃 Accidentes con Fuga (Hit and Run)": "/*\n Filtramos los accidentes donde\n hubo fuga y mostramos el nivel de daño\n*/\nSELECT TOP 100 \n    CRASH_DATE, \n    DAMAGE, \n    HIT_AND_RUN_I \nFROM CRASH \nWHERE HIT_AND_RUN_I = 'Y'\nORDER BY CRASH_DATE DESC;",
    "🚦 Dispositivos de Control de Tráfico": "SELECT \n    TC.TRAFFIC_CONTROL_DEVICE,\n    COUNT(C.CRASH_RECORD_ID) AS Numero_Crash\nFROM CRASH C\nJOIN ROAD R ON C.ROAD_ID = R.ROAD_ID\nJOIN TRAFFIC_CONTROL TC ON R.TRAFFIC_CONTROL_ID = TC.TRAFFIC_CONTROL_ID\nGROUP BY TC.TRAFFIC_CONTROL_DEVICE\nORDER BY Numero_Crash DESC;"
}

# --- REPORTES ACADÉMICOS (Semanas 6 a 11) ---
# Diccionario estructurado con la consulta y la configuración ideal de su gráfico
REPORTES_ACADEMICOS = {
    "S6-7: Mayor cantidad de lesionados por tipo de accidente": {
        "sql": """SELECT c.crash_type AS Tipo_Accidente, SUM(i.injuries_total) AS Total_Lesionados
FROM CRASH c
INNER JOIN INJURIES i ON c.crash_record_id = i.crash_record_id
GROUP BY c.crash_type
ORDER BY Total_Lesionados DESC;""",
        "chart": "bar", "x": "Tipo_Accidente", "y": "Total_Lesionados", "color": "Tipo_Accidente"
    },
    "S6-7: Calles con accidentes y fuga (Notificados a policía)": {
        "sql": """SELECT DISTINCT l.street_name AS Nombre_Calle
FROM CRASH c
INNER JOIN LOCATION l ON c.location_id = l.location_id
WHERE c.hit_and_run_i = 'Y' AND c.date_police_notified IS NOT NULL
ORDER BY Nombre_Calle;""",
        "chart": "none" # Solo es una lista descriptiva
    },
    "S6-7: Condiciones de pavimento con velocidad > 35 mph": {
        "sql": """SELECT co.roadway_surface_cond AS Condicion_Superficie, AVG(r.posted_speed_limit) AS Velocidad_Promedio
FROM CRASH c
INNER JOIN CONDITIONS co ON c.conditions_id = co.conditions_id
INNER JOIN ROAD r ON c.road_id = r.road_id
GROUP BY co.roadway_surface_cond
HAVING AVG(r.posted_speed_limit) > 20
ORDER BY Velocidad_Promedio DESC;""",
        "chart": "bar", "x": "Condicion_Superficie", "y": "Velocidad_Promedio", "color": "Condicion_Superficie"
    },
    "S6-7: Climas con > 10,000 accidentes graves y múltiples vehículos": {
        "sql": """SELECT w.weather_condition AS Condicion_Climatica, COUNT(c.crash_record_id) AS Total_Accidentes
FROM CRASH c
INNER JOIN WEATHER w ON c.weather_id = w.weather_id
WHERE c.damage = 'OVER $1,500' AND c.num_units >= 2
GROUP BY w.weather_condition
HAVING COUNT(c.crash_record_id) > 10000
ORDER BY Total_Accidentes DESC;""",
        "chart": "pie", "x": "Condicion_Climatica", "y": "Total_Accidentes", "color": None
    },
    "S9: Causas de accidente superiores al promedio general": {
        "sql": """WITH AccidentesPorCausa AS (
    SELECT cc.cause_description AS Descripcion_Causa, COUNT(*) AS Total_Accidentes
    FROM CRASH_CAUSE_DETAIL ccd
    INNER JOIN CAUSE_CATALOG cc ON ccd.cause_id = cc.cause_id
    GROUP BY cc.cause_description
)
SELECT * FROM AccidentesPorCausa
WHERE Total_Accidentes > (SELECT AVG(Total_Accidentes * 1.0) FROM AccidentesPorCausa)
ORDER BY Total_Accidentes DESC;""",
        "chart": "bar", "x": "Descripcion_Causa", "y": "Total_Accidentes", "color": "Total_Accidentes"
    },
    "S9: Accidentes con lesionados superior al promedio de su clima": {
        "sql": """SELECT c.crash_record_id AS ID_Accidente, w.weather_condition AS Condicion_Climatica, i.injuries_total AS Total_Lesionados
FROM CRASH c
INNER JOIN WEATHER w ON c.weather_id = w.weather_id
INNER JOIN INJURIES i ON c.crash_record_id = i.crash_record_id
WHERE i.injuries_total > (
    SELECT AVG(i2.injuries_total * 1.0) FROM CRASH c2
    INNER JOIN INJURIES i2 ON c2.crash_record_id = i2.crash_record_id
    WHERE c2.weather_id = c.weather_id
);""",
        "chart": "scatter", "x": "Condicion_Climatica", "y": "Total_Lesionados", "color": "Condicion_Climatica"
    },
    "S9: Calles con más de un accidente con lesiones fatales": {
        "sql": """SELECT DISTINCT l.street_name AS Nombre_Calle
FROM LOCATION l
WHERE EXISTS (
    SELECT 1 FROM CRASH c
    INNER JOIN INJURIES i ON c.crash_record_id = i.crash_record_id
    WHERE c.location_id = l.location_id AND i.injuries_fatal > 1
)
ORDER BY Nombre_Calle;""",
        "chart": "none"
    },
    "S9: Condiciones climáticas sin fugas de conductor": {
        "sql": """SELECT DISTINCT w.weather_condition AS Condicion_Climatica
FROM WEATHER w
WHERE NOT EXISTS (
    SELECT 1 FROM CRASH c
    WHERE c.weather_id = w.weather_id AND c.hit_and_run_i = 'Y'
)
ORDER BY Condicion_Climatica;""",
        "chart": "none"
    },
    "S10: Tiempo promedio de notificación a policía por tipo (Horas)": {
        "sql": """SELECT crash_type AS Tipo_Accidente, AVG(DATEDIFF(HOUR, crash_date, date_police_notified) * 1.0) AS Promedio_Horas
FROM CRASH
WHERE date_police_notified IS NOT NULL
GROUP BY crash_type
ORDER BY Promedio_Horas DESC;""",
        "chart": "bar", "x": "Tipo_Accidente", "y": "Promedio_Horas", "color": "Promedio_Horas"
    },
    "S10: Accidentes por mes del año": {
        "sql": """SELECT FORMAT(crash_date, 'yyyy-MM') AS Periodo, COUNT(*) AS Total_Accidentes
FROM CRASH
GROUP BY FORMAT(crash_date, 'yyyy-MM')
ORDER BY Periodo;""",
        "chart": "line", "x": "Periodo", "y": "Total_Accidentes", "color": None
    },
    "S10: Tiempo promedio de notificación por trimestre y tipo (Minutos)": {
        "sql": """SELECT CHOOSE(DATEPART(QUARTER, c.crash_date), 'Q1','Q2','Q3','Q4') AS Trimestre,
       c.crash_type AS Tipo_Accidente, AVG(DATEDIFF(MINUTE, c.crash_date, c.date_police_notified) * 1.0) AS Promedio_Minutos
FROM CRASH c
WHERE c.date_police_notified IS NOT NULL
GROUP BY DATEPART(QUARTER, c.crash_date), c.crash_type
ORDER BY Trimestre, Promedio_Minutos DESC;""",
        "chart": "bar", "x": "Trimestre", "y": "Promedio_Minutos", "color": "Tipo_Accidente"
    },
    "S10: Climas con alta severidad priorizados para análisis": {
        "sql": """SELECT w.weather_condition AS Condicion_Climatica, AVG(i.injuries_total * 1.0) AS Promedio_Lesionados, COUNT(*) AS Total_Accidentes
FROM CRASH c
INNER JOIN WEATHER w ON c.weather_id = w.weather_id
INNER JOIN INJURIES i ON c.crash_record_id = i.crash_record_id
GROUP BY w.weather_condition
ORDER BY CASE WHEN AVG(i.injuries_total * 1.0) >= 2 THEN 1 WHEN AVG(i.injuries_total * 1.0) >= 1 THEN 2 ELSE 3 END,
Promedio_Lesionados DESC;""",
        "chart": "scatter", "x": "Total_Accidentes", "y": "Promedio_Lesionados", "color": "Condicion_Climatica"
    },
    "S11: Calles con mayor concentración (Top 5 por tipo)": {
        "sql": """WITH RankingCalles AS (
    SELECT c.crash_type AS Tipo_Accidente, l.street_name AS Nombre_Calle, COUNT(*) AS Total_Accidentes,
           DENSE_RANK() OVER (PARTITION BY c.crash_type ORDER BY COUNT(*) DESC) AS ranking
    FROM CRASH c
    INNER JOIN LOCATION l ON c.location_id = l.location_id
    GROUP BY c.crash_type, l.street_name
)
SELECT * FROM RankingCalles
WHERE ranking <= 5
ORDER BY Tipo_Accidente, ranking;""",
        "chart": "bar", "x": "Nombre_Calle", "y": "Total_Accidentes", "color": "Tipo_Accidente"
    },
    "S11: Evolución de accidentes mes a mes (MoM)": {
        "sql": """WITH AccidentesMensuales AS (
    SELECT YEAR(crash_date) AS anio_num, MONTH(crash_date) AS mes, COUNT(*) AS Total_Accidentes
    FROM CRASH
    GROUP BY YEAR(crash_date), MONTH(crash_date)
)
SELECT CAST(anio_num AS VARCHAR(4)) AS Anio, mes AS Mes, Total_Accidentes,
       LAG(Total_Accidentes) OVER(ORDER BY anio_num, mes) AS Accidentes_Mes_Anterior,
       Total_Accidentes - LAG(Total_Accidentes) OVER(ORDER BY anio_num, mes) AS Diferencia
FROM AccidentesMensuales
ORDER BY anio_num, Mes;""",
        "chart": "line", "x": "Mes", "y": "Total_Accidentes", "color": "Anio"
    },
    "S11: Participación por condición climática": {
        "sql": """SELECT w.weather_condition AS Condicion_Climatica, COUNT(*) AS Total_Accidentes,
       FORMAT(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 'N2') + '%' AS Participacion
FROM CRASH c
INNER JOIN WEATHER w ON c.weather_id = w.weather_id
GROUP BY w.weather_condition
ORDER BY Total_Accidentes DESC;""",
        "chart": "pie", "x": "Condicion_Climatica", "y": "Total_Accidentes", "color": None
    }
}