# Libraries
import pandas as pd
from datetime import timedelta

# --------------------------------------------------------------
# OT dataset
# --------------------------------------------------------------

# Diccionario OT Orden de Trabajo
dtype_dic_wotmaq = {
    'wonum': str,
    'assetnum': str,
    'actstart': str,
    'schedstart': str,
    'targstartdate': str
    }

# Diccionario meses
meses = {
'ene': '01',
'feb': '02',
'mar': '03',
'abr': '04',
'may': '05',
'jun': '06',
'jul': '07',
'ago': '08',
'sep': '09',
'oct': '10',
'nov': '11',
'dic': '12'
}

# Leer archivos
wot_maq_df = pd.read_csv("../../data/external/WOTMAQ.csv", sep=";", dtype=dtype_dic_wotmaq)

# --------------------------------------------------------------
# Tratamiento de Fechas
# --------------------------------------------------------------

# Columnas con fechas
columns = wot_maq_df.columns[2:]
# Transformar cada columna a formato fecha
for col in columns:
    # Reemplazar mes
    wot_maq_df[col] = wot_maq_df[col].replace(meses, regex=True)
    # Reemplazar AM/PM en español
    wot_maq_df[col] = (wot_maq_df[col].str.replace(' a.m.', ' AM', regex=False).str.replace(' p.m.', ' PM', regex=False))
    # Convertir
    wot_maq_df[col] = pd.to_datetime(wot_maq_df[col],format='%m %d, %Y %I:%M %p')

# --------------------------------------------------------------
# Estructurar data
# --------------------------------------------------------------

# Eliminar filas donde assetnum sea NaN
wot_maq_df = wot_maq_df[wot_maq_df['assetnum'].notna()]
# Fecha inicio
fecha_ini = pd.to_datetime('2020-01-01')
# Fecha hoy
hoy = pd.Timestamp.today()
# Filtrar
wot_maq_df = wot_maq_df[(wot_maq_df['schedstart'] >= fecha_ini) & (wot_maq_df['schedstart'] <= hoy)]

# Funcion para definir fecha de inicio de OT
def startdate(row):
    # Si actstart es menor a fecha_ini, es nula o es posterior al día de hoy, que sea schedstart
    if (row['actstart'] < fecha_ini) | (pd.isna(row['actstart']) | (row['actstart'] > hoy)):
        return row['schedstart']
    # Para todo lo demás que sea actstart
    else:
        return row['actstart']

wot_maq_df['startdate'] = wot_maq_df.apply(startdate, axis=1)

# Eliminar columnas
del wot_maq_df['actstart']
del wot_maq_df['schedstart']
del wot_maq_df['targstartdate']

# --------------------------------------------------------------
# Preparación de datasets
# --------------------------------------------------------------

# Carga de registros de utilización depurados
bit_df = pd.read_pickle("../../data/interim/02_outliers_removed_chauvenets.pkl")
bit_df = bit_df.dropna()
bit_df = bit_df.reset_index()

# Ventana de análisis posterior a cada OT
days = 7

# Ordenamiento cronológico de la bitácora por activo
bit = bit_df.sort_values(["activo", "FECHA"]).copy()
# Selección de las variables mínimas necesarias
ot = wot_maq_df[["wonum", "assetnum", "startdate"]].copy()

# Conversión de identificadores a texto para evitar incompatibilidades durante los merge_asof
bit["activo"] = bit["activo"].astype(str)
ot["assetnum"] = ot["assetnum"].astype(str)

# Conversión explícita de fechas a datetime64[ns]
bit["FECHA"] = pd.to_datetime(bit["FECHA"]).astype("datetime64[ns]")
ot["startdate"] = pd.to_datetime(ot["startdate"]).astype("datetime64[ns]")

# --------------------------------------------------------------
# Distancia acumulada por activo
# --------------------------------------------------------------

# Se calcula el acumulado histórico de delta para cada activo.
# Esto permite obtener el movimiento entre dos fechas por diferencia de acumulados.
bit["cum_delta"] = bit.groupby("activo")["delta"].cumsum()

# Fecha final posterior a la OT.
# Esto permite obtener cuánto se movió el equipo dentro entre ambas fechas
ot["enddate"] = ot["startdate"] + timedelta(days=days)
ot["enddate"] = pd.to_datetime(ot["enddate"]).astype("datetime64[ns]")

# ------------------------------------------------------------------
# Acumulado hasta enddate
# ------------------------------------------------------------------

# Para cada OT se busca el último registro disponible
# de bitácora anterior o igual a enddate.
# A “backward” search selects the last row in the right DataFrame whose ‘on’ key
# is less than or equal to the left’s key.

# Va recorriendo fila a fila en tabla "ot"
# La fila en "bit.assetnum", debe coincidir con el ot.activo
# y la bit.FECHA sea igual o menor a bit.enddate

cum_end = pd.merge_asof(
    ot.sort_values("enddate"),
    bit[["activo", "FECHA", "cum_delta"]].sort_values("FECHA"),
    left_on="enddate",
    right_on="FECHA",
    left_by="assetnum",
    right_by="activo",
    direction="backward"
)[["wonum", "cum_delta"]]

# Los Nan corresponden a Activos Menores,
# activos sin movimientos anterior al enddate,
# o activos sin movimientos (semiremolque)
cum_end = cum_end.rename(columns={"cum_delta": "cum_end"})

# ------------------------------------------------------------------
# Acumulado inmediatamente antes de startdate
# ------------------------------------------------------------------

# Se obtiene el acumulado justo antes del inicio de la orden de trabajo.

cum_ini = pd.merge_asof(
    ot.sort_values("startdate"),
    bit[["activo", "FECHA", "cum_delta"]].sort_values("FECHA"),
    left_on="startdate",
    right_on="FECHA",
    left_by="assetnum",
    right_by="activo",
    direction="backward"
)[["wonum", "cum_delta"]]

cum_ini = cum_ini.rename(columns={"cum_delta": "cum_ini"})

# --------------------------------------------------------------
# Cálculo del movimiento ocurrido dentro de la ventana
# --------------------------------------------------------------

# Consolidación de resultados
result = (
    ot[["wonum", "assetnum", "startdate"]]
    .merge(cum_end, on="wonum")
    .merge(cum_ini, on="wonum")
)

# Eliminar Nan
result = result.dropna()

# Calcular diferencia entre acumulados
result["delta_cum"] = result["cum_end"] - result["cum_ini"]

# OTs sin movimiento en los días posteriores
ot_sin_mov_df = result[result["delta_cum"] == 0]

# --------------------------------------------------------------
# Generación del dataset final
# --------------------------------------------------------------

# Carga del universo completo de órdenes de trabajo
ot_df = pd.read_pickle("../../reports/OTmaquinarias.pkl")

# Conserva únicamente OT asociadas a períodos
# de inmovilidad posteriores a la intervención
mc_ot_df = pd.merge(ot_df,
                    ot_sin_mov_df[['wonum', 'startdate']],
                    left_on='WONUM',
                    right_on='wonum',
                    how='inner')

# Se reemplaza la fecha original de reporte por la fecha
# efectiva utilizada para el análisis
del mc_ot_df['REPORTDATE']
del mc_ot_df['wonum']
mc_ot_df = mc_ot_df.rename(columns={"startdate": "REPORTDATE"})

# Exportación del conjunto de OT candidatas a
# mantenimiento correctivo basado en inmovilización
# posterior del equipo.
mc_ot_df.to_pickle('../../reports/OTmaquinariasMCWOTMAQ.pkl')
