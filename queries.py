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

# --- REPORTES ACADÉMICOS (Semanas 6 a 13) ---
REPORTES_ACADEMICOS = {
    "S6-7: Mayor cantidad de lesionados por tipo de accidente": {
        "sql": """SELECT c.crash_type, SUM(i.injuries_total) AS total_lesionados
FROM CRASH c
INNER JOIN INJURIES i ON c.crash_record_id = i.crash_record_id
GROUP BY c.crash_type
ORDER BY total_lesionados DESC;""",
        "chart": "bar", "x": "crash_type", "y": "total_lesionados", "color": "crash_type"
    },
    "S6-7: Calles con accidentes y fuga (Notificados a policía)": {
        "sql": """SELECT DISTINCT l.street_name
FROM CRASH c
INNER JOIN LOCATION l ON c.location_id = l.location_id
WHERE c.hit_and_run_i = 'Y' AND c.date_police_notified IS NOT NULL
ORDER BY l.street_name;""",
        "chart": "none"
    },
    "S6-7: Condiciones de pavimento con velocidad > 35 mph": {
        "sql": """SELECT co.roadway_surface_cond, AVG(r.posted_speed_limit) AS velocidad_promedio
FROM CRASH c
INNER JOIN CONDITIONS co ON c.conditions_id = co.conditions_id
INNER JOIN ROAD r ON c.road_id = r.road_id
GROUP BY co.roadway_surface_cond
HAVING AVG(r.posted_speed_limit) > 20
ORDER BY velocidad_promedio DESC;""",
        "chart": "bar", "x": "roadway_surface_cond", "y": "velocidad_promedio", "color": "roadway_surface_cond"
    },
    "S6-7: Climas con > 10,000 accidentes graves y múltiples vehículos": {
        "sql": """SELECT w.weather_condition, COUNT(c.crash_record_id) AS total_accidentes
FROM CRASH c
INNER JOIN WEATHER w ON c.weather_id = w.weather_id
WHERE c.damage = 'OVER $1,500' AND c.num_units >= 2
GROUP BY w.weather_condition
HAVING COUNT(c.crash_record_id) > 10000
ORDER BY total_accidentes DESC;""",
        "chart": "pie", "x": "weather_condition", "y": "total_accidentes", "color": None
    },
    "S6-7: Choques múltiples (> 3 vehículos) con fuga del conductor": {
        "sql": """SELECT crash_type, COUNT(*) AS volumen_critico_fugas
FROM CRASH
WHERE num_units > 3 AND hit_and_run_i = 'Y'
GROUP BY crash_type
ORDER BY volumen_critico_fugas DESC;""",
        "chart": "bar", "x": "crash_type", "y": "volumen_critico_fugas", "color": "crash_type"
    },
    "S9: Causas de accidente superiores al promedio general": {
        "sql": """WITH AccidentesPorCausa AS (
    SELECT cc.cause_description, COUNT(*) AS total_accidentes
    FROM CRASH_CAUSE_DETAIL ccd
    INNER JOIN CAUSE_CATALOG cc ON ccd.cause_id = cc.cause_id
    GROUP BY cc.cause_description
)
SELECT * FROM AccidentesPorCausa
WHERE total_accidentes > (SELECT AVG(total_accidentes * 1.0) FROM AccidentesPorCausa)
ORDER BY total_accidentes DESC;""",
        "chart": "bar", "x": "cause_description", "y": "total_accidentes", "color": "total_accidentes"
    },
    "S9: Accidentes con lesionados superior al promedio de su clima": {
        "sql": """SELECT c.crash_record_id, w.weather_condition, i.injuries_total
FROM CRASH c
INNER JOIN WEATHER w ON c.weather_id = w.weather_id
INNER JOIN INJURIES i ON c.crash_record_id = i.crash_record_id
WHERE i.injuries_total > (
    SELECT AVG(i2.injuries_total * 1.0) 
    FROM CRASH c2
    INNER JOIN INJURIES i2 ON c2.crash_record_id = i2.crash_record_id
    WHERE c2.weather_id = c.weather_id
);""",
        "chart": "scatter", "x": "weather_condition", "y": "injuries_total", "color": "weather_condition"
    },
    "S9: Calles con más de un accidente con lesiones fatales": {
        "sql": """SELECT DISTINCT l.street_name
FROM LOCATION l
WHERE EXISTS (
    SELECT 1 FROM CRASH c
    INNER JOIN INJURIES i ON c.crash_record_id = i.crash_record_id
    WHERE c.location_id = l.location_id AND i.injuries_fatal > 1
)
ORDER BY l.street_name;""",
        "chart": "none"
    },
    "S9: Condiciones climáticas sin fugas de conductor": {
        "sql": """SELECT DISTINCT w.weather_condition
FROM WEATHER w
WHERE NOT EXISTS (
    SELECT 1 FROM CRASH c
    WHERE c.weather_id = w.weather_id AND c.hit_and_run_i = 'Y'
)
ORDER BY w.weather_condition;""",
        "chart": "none"
    },
    "S9: Climas con siniestralidad superior al promedio general": {
        "sql": """SELECT w.weather_condition, COUNT(c.crash_record_id) AS total_accidentes_clima
FROM CRASH c
INNER JOIN WEATHER w ON c.weather_id = w.weather_id
GROUP BY w.weather_condition
HAVING COUNT(c.crash_record_id) > (
    SELECT AVG(sub.accidentes_por_clima)
    FROM (
        SELECT COUNT(crash_record_id) AS accidentes_por_clima
        FROM CRASH
        GROUP BY weather_id
    ) sub
)
ORDER BY total_accidentes_clima DESC;""",
        "chart": "bar", "x": "weather_condition", "y": "total_accidentes_clima", "color": "weather_condition"
    },
    "S10: Tiempo promedio de notificación a policía por tipo (Horas)": {
        "sql": """SELECT crash_type, AVG(DATEDIFF(HOUR, crash_date, date_police_notified) * 1.0) AS promedio_horas
FROM CRASH
WHERE date_police_notified IS NOT NULL
GROUP BY crash_type
ORDER BY promedio_horas DESC;""",
        "chart": "bar", "x": "crash_type", "y": "promedio_horas", "color": "promedio_horas"
    },
    "S10: Accidentes por mes del año": {
        "sql": """SELECT FORMAT(crash_date, 'yyyy-MM') AS periodo, COUNT(*) AS total_accidentes
FROM CRASH
GROUP BY FORMAT(crash_date, 'yyyy-MM')
ORDER BY periodo;""",
        "chart": "line", "x": "periodo", "y": "total_accidentes", "color": None
    },
    "S10: Tiempo promedio de notificación por trimestre y tipo (Minutos)": {
        "sql": """SELECT CHOOSE(DATEPART(QUARTER, c.crash_date), 'Q1','Q2','Q3','Q4') AS trimestre,
       c.crash_type, AVG(DATEDIFF(MINUTE, c.crash_date, c.date_police_notified) * 1.0) AS promedio_minutos
FROM CRASH c
WHERE c.date_police_notified IS NOT NULL
GROUP BY DATEPART(QUARTER, c.crash_date), c.crash_type
ORDER BY trimestre, promedio_minutos DESC;""",
        "chart": "bar", "x": "trimestre", "y": "promedio_minutos", "color": "crash_type"
    },
    "S10: Climas con alta severidad priorizados para análisis": {
        "sql": """SELECT w.weather_condition, AVG(i.injuries_total * 1.0) AS promedio_lesionados, COUNT(*) AS total_accidentes
FROM CRASH c
INNER JOIN WEATHER w ON c.weather_id = w.weather_id
INNER JOIN INJURIES i ON c.crash_record_id = i.crash_record_id
GROUP BY w.weather_condition
ORDER BY CASE WHEN AVG(i.injuries_total * 1.0) >= 2 THEN 1 WHEN AVG(i.injuries_total * 1.0) >= 1 THEN 2 ELSE 3 END,
promedio_lesionados DESC;""",
        "chart": "scatter", "x": "total_accidentes", "y": "promedio_lesionados", "color": "weather_condition"
    },
    "S10: Brecha temporal promedio de notificación según gravedad del daño": {
        "sql": """SELECT damage, AVG(DATEDIFF(MINUTE, CAST(crash_date AS DATETIME), CAST(date_police_notified AS DATETIME))) AS promedio_minutos_notificacion
FROM CRASH
WHERE crash_date IS NOT NULL AND date_police_notified IS NOT NULL
GROUP BY damage
ORDER BY promedio_minutos_notificacion DESC;""",
        "chart": "bar", "x": "damage", "y": "promedio_minutos_notificacion", "color": "damage"
    },
    "S11: Calles con mayor concentración por tipo de accidente": {
        "sql": """WITH RankingCalles AS (
    SELECT c.crash_type, l.street_name, COUNT(*) AS total_accidentes,
           DENSE_RANK() OVER (PARTITION BY c.crash_type ORDER BY COUNT(*) DESC) AS ranking
    FROM CRASH c
    INNER JOIN LOCATION l ON c.location_id = l.location_id
    GROUP BY c.crash_type, l.street_name
)
SELECT * FROM RankingCalles
WHERE ranking <= 5
ORDER BY crash_type, ranking;""",
        "chart": "bar", "x": "street_name", "y": "total_accidentes", "color": "crash_type"
    },
    "S11: Evolución de accidentes mes a mes (MoM)": {
        "sql": """WITH AccidentesMensuales AS (
    SELECT YEAR(crash_date) AS anio, MONTH(crash_date) AS mes, COUNT(*) AS total_accidentes
    FROM CRASH
    GROUP BY YEAR(crash_date), MONTH(crash_date)
)
SELECT anio, mes, total_accidentes,
       LAG(total_accidentes) OVER(ORDER BY anio, mes) AS accidentes_mes_anterior,
       total_accidentes - LAG(total_accidentes) OVER(ORDER BY anio, mes) AS diferencia
FROM AccidentesMensuales
ORDER BY anio, mes;""",
        "chart": "line", "x": "mes", "y": "total_accidentes", "color": "anio"
    },
    "S11: Participación por condición climática": {
        "sql": """SELECT w.weather_condition, COUNT(*) AS total_accidentes,
       FORMAT(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 'N2') + '%' AS participacion
FROM CRASH c
INNER JOIN WEATHER w ON c.weather_id = w.weather_id
GROUP BY w.weather_condition
ORDER BY total_accidentes DESC;""",
        "chart": "pie", "x": "weather_condition", "y": "total_accidentes", "color": None
    },
    "S11: Top 3 causas principales más peligrosas por tipo de choque": {
        "sql": """WITH BaseSiniestros AS (
    SELECT c.crash_type, cc.cause_description, SUM(i.injuries_total) AS total_personas_lesionadas
    FROM CRASH c
    INNER JOIN CRASH_CAUSE_DETAIL ccd ON c.crash_record_id = ccd.crash_record_id
    INNER JOIN CAUSE_CATALOG cc ON ccd.cause_id = cc.cause_id
    INNER JOIN INJURIES i ON c.crash_record_id = i.crash_record_id
    GROUP BY c.crash_type, cc.cause_description
),
RankingCausas AS (
    SELECT crash_type, cause_description, total_personas_lesionadas,
           DENSE_RANK() OVER (PARTITION BY crash_type ORDER BY total_personas_lesionadas DESC) AS posicion_ranking                                                                                                             
    FROM BaseSiniestros
)
SELECT crash_type, cause_description, total_personas_lesionadas, posicion_ranking
FROM RankingCausas
WHERE posicion_ranking <= 3;""",
        "chart": "bar", "x": "cause_description", "y": "total_personas_lesionadas", "color": "crash_type"
    },
    "S11: Reporte gerencial de accidentabilidad acumulada (YTD) por vía": {
        "sql": """WITH ResumenMensual AS (
    SELECT r.trafficway_type, YEAR(CAST(c.crash_date AS DATETIME)) AS anio, MONTH(CAST(c.crash_date AS DATETIME)) AS mes,
           COUNT(c.crash_record_id) AS siniestros_del_mes
    FROM CRASH c
    INNER JOIN ROAD r ON c.road_id = r.road_id
    WHERE c.crash_date IS NOT NULL
    GROUP BY r.trafficway_type, YEAR(CAST(c.crash_date AS DATETIME)), MONTH(CAST(c.crash_date AS DATETIME))
)
SELECT trafficway_type, anio, mes, siniestros_del_mes,
       SUM(siniestros_del_mes) OVER (PARTITION BY trafficway_type, anio ORDER BY mes) AS acumulado_historico_YTD
FROM ResumenMensual
ORDER BY trafficway_type, anio, mes;""",
        "chart": "line", "x": "mes", "y": "acumulado_historico_YTD", "color": "trafficway_type"
    },
    "S13: PIVOT - Accidentes por clima y año dinámico": {
        "sql": """DECLARE @cols NVARCHAR(MAX);
DECLARE @query NVARCHAR(MAX);

SELECT @cols = STRING_AGG(QUOTENAME(CAST(anio AS VARCHAR(4))), ',') WITHIN GROUP (ORDER BY anio)
FROM (SELECT DISTINCT YEAR(crash_date) AS anio FROM CRASH) AS A;

SET @query = N'
SELECT * FROM (
    SELECT w.weather_condition, YEAR(c.crash_date) AS anio, c.crash_record_id
    FROM CRASH c
    INNER JOIN WEATHER w ON c.weather_id = w.weather_id
) AS Origen
PIVOT (
    COUNT(crash_record_id) FOR anio IN (' + @cols + N')
) AS P
ORDER BY weather_condition;';

EXEC sp_executesql @query;""",
        "chart": "none"
    },
    "S13: UNPIVOT - Total de lesionados por tipo de lesión": {
        "sql": """SELECT tipo_lesion, SUM(Cantidad) AS total_lesionados
FROM (
    SELECT injuries_fatal, injuries_incapacitating, injuries_non_incapacitating, injuries_no_indication
    FROM INJURIES
) AS Origen
UNPIVOT (
    Cantidad FOR Tipo_Lesion IN (injuries_fatal, injuries_incapacitating, injuries_non_incapacitating, injuries_no_indication)
) AS U
GROUP BY Tipo_Lesion
ORDER BY total_lesionados DESC;""",
        "chart": "pie", "x": "tipo_lesion", "y": "total_lesionados", "color": None
    },
    "S13: UNPIVOT - Meta trimestral vs cantidad real registrada": {
        "sql": """WITH MetaAccidentes AS (
    SELECT * FROM (VALUES (2500.0, 2600.0, 2400.0, 2700.0)) AS T(Q1, Q2, Q3, Q4)
),
MetaNormalizada AS (
    SELECT Trimestre, Meta FROM MetaAccidentes
    UNPIVOT (Meta FOR Trimestre IN ([Q1],[Q2],[Q3],[Q4])) AS U
)
SELECT M.Trimestre, M.Meta, COUNT(c.crash_record_id) AS Accidentes_Reales,
       COUNT(c.crash_record_id) - M.Meta AS Diferencia
FROM MetaNormalizada M
LEFT JOIN CRASH c ON CHOOSE(DATEPART(QUARTER, c.crash_date), 'Q1','Q2','Q3','Q4') = M.Trimestre
GROUP BY M.Trimestre, M.Meta
ORDER BY M.Trimestre;""",
        "chart": "bar", "x": "Trimestre", "y": "Accidentes_Reales", "color": None
    },
    "S13: PIVOT - Evolución de accidentes por clima (Corte Anual)": {
        "sql": """DECLARE @RefMes INT = 6;  -- hasta junio
DECLARE @RefDia INT = 30; -- día 30

SELECT weather_condition, ISNULL([2021], 0) AS Corte2021, ISNULL([2022], 0) AS Corte2022, ISNULL([2023], 0) AS Corte2023
FROM (
    SELECT w.weather_condition, YEAR(c.crash_date) AS anio, c.crash_record_id
    FROM CRASH c
    INNER JOIN WEATHER w ON c.weather_id = w.weather_id
    WHERE (MONTH(c.crash_date) < @RefMes) OR (MONTH(c.crash_date) = @RefMes AND DAY(c.crash_date) <= @RefDia)
) AS Origen
PIVOT (
    COUNT(crash_record_id) FOR anio IN ([2021],[2022],[2023])
) AS P
ORDER BY weather_condition;""",
        "chart": "none"
    },
    "S13: PIVOT - Accidentes por tipo según condición de calzada": {
        "sql": """SELECT *
FROM (
    SELECT c.crash_type, co.roadway_surface_cond, c.crash_record_id
    FROM CRASH c
    INNER JOIN CONDITIONS co ON c.conditions_id = co.conditions_id
) AS Origen
PIVOT (
    COUNT(crash_record_id) FOR roadway_surface_cond IN ([DRY],[WET],[SNOW OR SLUSH],[ICE],[UNKNOWN])
) AS P
ORDER BY crash_type;""",
        "chart": "none"
    }
}