# Libraries
import pandas as pd

# --------------------------------------------------------------
# Carga de datos
# --------------------------------------------------------------

# Carga de la bitácora de utilización depurada
bit_df = pd.read_pickle("../../data/interim/02_outliers_removed_chauvenets.pkl")
# Eliminación de registros incompletos
bit_df = bit_df.dropna()
# Restauración del índice y ordenamiento temporal
bit_df = bit_df.reset_index()
bit_df = bit_df.sort_values(by=["sigla", "FECHA"])

# --------------------------------------------------------------
# Construcción de serie temporal continua
# --------------------------------------------------------------

# Genera un calendario diario completo entre la primera
# y última fecha disponible en la bitácora
full_dates = pd.date_range(
    start=bit_df["FECHA"].min(), end=bit_df["FECHA"].max(), freq="D"
)

# Obtiene todas las siglas existentes
all_siglas = bit_df["sigla"].unique()

# Construye una grilla completa de combinaciones
# EQUIPO x FECHA
full_index = pd.MultiIndex.from_product(
    [all_siglas, full_dates], names=["sigla", "FECHA"]
)

# Expande la bitácora para asegurar que exista un
# registro por día para cada equipo.
bit_df = bit_df.set_index(["sigla", "FECHA"]).reindex(full_index).reset_index()

# Se asume que los días sin registros corresponden
# a ausencia de movimiento.
bit_df["delta"] = bit_df["delta"].fillna(0)

# --------------------------------------------------------------
# Cálculo de movimiento futuro
# --------------------------------------------------------------

# Ventana de observación
days = 14

# Se calcula cuánto movimiento tiene el equipo durante los siguientes 14 días.
# shift(-days) desplaza la ventana hacia adelante y rolling() acumula el total de movimiento futuro.
bit_df["delta_hist"] = bit_df.groupby("sigla")["delta"].shift(-days).rolling(days).sum()

# Elimina registros para los cuales no existe información suficiente para calcular la ventana completa
bit_df = bit_df.dropna(subset=["delta_hist"])

# --------------------------------------------------------------
# Identificación de eventos candidatos a mantenimiento correctivo
# --------------------------------------------------------------
contador = 0


def ismc(row):
    global contador
    # Si existe movimiento y posteriormente el equipo permanece inmóvil
    # durante los siguientes 14 días,
    # entonces se marca como potencial evento asociado
    # a mantenimiento correctivo.
    if (row["delta"] > 0) and row["delta_hist"] == 0:
        return "Si"
    else:
        return "No"
    print(contador)
    contador += 1


# Evaluación de todos los registros
bit_df["MC"] = bit_df.apply(ismc, axis=1)

# Conserva únicamente los eventos identificados
# como candidatos a mantención correctiva
ot_df = bit_df[bit_df["MC"] == "Si"]

# --------------------------------------------------------------
# Construcción de estructura compatible con OT
# --------------------------------------------------------------

# Se agrega una columna de costo para mantener
# compatibilidad estructural con otros datasets de OT
ot_df["COSTO"] = 0

# Renombramiento de columnas para homologar nombres
# con el modelo utilizado en el resto del proyecto
ot_df = ot_df.rename(
    columns={"FECHA": "REPORTDATE", "sigla": "SIGLA", "activo": "WONUM"}
)

# --------------------------------------------------------------
# Eliminación de variables no requeridas
# --------------------------------------------------------------

del ot_df["medidor"]
del ot_df["ini"]
del ot_df["fin"]
del ot_df["region"]
del ot_df["set"]
del ot_df["type"]
del ot_df["loc"]
del ot_df["ulectura"]
del ot_df["delta"]
del ot_df["delta_hist"]
del ot_df["MC"]
del ot_df["year"]
del ot_df["bit-year"]

# --------------------------------------------------------------
# Exportación
# --------------------------------------------------------------

# Dataset de eventos candidatos a mantenimiento correctivo
# inferidos únicamente desde patrones de utilización
# e inmovilización operacional.

ot_df.to_pickle("../../reports/OTmaquinariasStopEvent.pkl")
