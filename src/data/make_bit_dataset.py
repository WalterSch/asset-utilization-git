# Librerías
import pandas as pd
from glob import glob

# --------------------------------------------------------------
# Bit dataset
# --------------------------------------------------------------

# Enlista todos los archivos .csv de la carpeta
files = glob("../../data/raw/bit/*.csv")

# Diccionario archivo bitácora
dtype_dic_bit = {
    "total_rec": str,
    "FOLIO": str,
    "INGRESO": str,
    "UBICP": str,
    "HERR": str,
    "SIGLA": str,
    "UBICH": str,
    "VIAJE": float,
    "OS": str,
    "OT": str,
    "CC": str,
    "FECHA": str,
    "INICIO": str,
    "DESTINO": str,
    "MEDIDOR": str,
    "HR_KM_INI": float,
    "HR_KM_FIN": float,
    "ESTADOMOTOR": str,
    "HORAINI": str,
    "HORAFIN": str,
    "RESPONSABLE": str,
    "RUT": str,
    "ESTADO": str,
    "agno": float,
}


# Función para leer datos
def read_data_from_files(files):
    # Dataframe vacío
    bit_df = pd.DataFrame()
    # Contador de archivos
    bit_set = 1
    # Ciclo for para leer todos los archivos en la carpeta
    for f in files:
        # Texto indica qué archivo está leyendo
        print(f"Leyendo archivo {bit_set}")
        # extraer region desde el nombre del archivo
        region = f.split("_")[1].replace("fos", "")[:2]
        # extraer ano desde el nombre del archivo
        ano = f.split("_")[1].replace("fos", "")[2:6]
        # leer archivo y asignarlo a df
        df = pd.read_csv(f, sep=";", dtype=dtype_dic_bit)
        # columna region
        df["region"] = region
        # columna ano
        df["ano"] = ano
        # columna set
        df["set"] = bit_set
        # contador +1
        bit_set += 1
        # concatenar a medida que se leen archivos a partir del dataframe vacío
        bit_df = pd.concat([bit_df, df])

    # fecha como index
    bit_df.index = pd.to_datetime(bit_df["FECHA"], format="%d/%m/%y")

    # eliminar filas innecesarias
    del bit_df["total_rec"]
    del bit_df["FOLIO"]
    del bit_df["INGRESO"]
    del bit_df["UBICP"]
    del bit_df["UBICH"]
    del bit_df["VIAJE"]
    del bit_df["OS"]
    del bit_df["OT"]
    del bit_df["CC"]
    del bit_df["INICIO"]
    del bit_df["DESTINO"]
    del bit_df["ESTADOMOTOR"]
    del bit_df["HORAINI"]
    del bit_df["HORAFIN"]
    del bit_df["RESPONSABLE"]
    del bit_df["RUT"]
    del bit_df["ESTADO"]
    del bit_df["agno"]
    del bit_df["FECHA"]

    # retornar df
    return bit_df


bit_df = read_data_from_files(files)

# --------------------------------------------------------------
# Estructurar data
# --------------------------------------------------------------

# Renombrar columnas
bit_df.columns = ["activo", "sigla", "medidor", "ini", "fin", "region", "ano", "set"]

# calcular delta movimiento fila a fila
bit_df["delta"] = bit_df["fin"] - bit_df["ini"]
bit_df = bit_df[bit_df["delta"] > 0]

# --------------------------------------------------------------
# Remuestrar data por día
# --------------------------------------------------------------

# calculo a realizar por columna
sampling = {
    "sigla": "last",
    "medidor": "last",
    "ini": "first",
    "fin": "last",
    "region": "last",
    "ano": "last",
    "set": "last",
    "delta": "sum",
}

# remuestreo por día y N° activo
data_resampled = (
    bit_df.groupby([pd.Grouper(freq="D"), "activo"])
    .agg(sampling)
    .dropna()
    .reset_index()
)

# --------------------------------------------------------------
# Tipología, ubicación, año adquisición, última lectura de activos
# --------------------------------------------------------------

# Diccionario archivo Registro Nacional de Maquinarias y Vehículos
dtype_dic_rnm = {
    "ASSETNUM": str,
    "DESCRIPTION": str,
    "LOCATION": str,
    "SIGLA": str,
    "STATUS": str,
    "ASSETTYPE": str,
    "PATENTE": str,
    "PURCHASEPRICE": float,
    "TIPOCOMBUST": str,
    "CAPESTANQUE": float,
    "RENDIMIENTO": float,
    "ASIGNACION": str,
    "TARIFAHORA": float,
    "VENDOR": str,
    "CLASE": str,
    "CLASSIFICATIONID": str,
    "GORE": str,
    "PARENT": str,
    "MEDIDOR": str,
    "UMEDIDA": str,
    "INSPECTOR": str,
    "AÃ‘O": str,
    "COLOR": str,
    "FECHABAJA": str,
    "FECHAREMATE": str,
    "FECHACOMP": str,
    "FECHATRASP": str,
    "LUGARREMA": str,
    "MARCA": str,
    "MODELO": str,
    "MOTOR": str,
    "SERIE": str,
    "SIGAC": str,
    "OBSERV": str,
    "PROTRASP": str,
    "POTENCIA": str,
    "RESBAJA": str,
    "RESCOMPRA": str,
    "TRACCION": str,
    "VALORREMA": str,
    "FECHA_FACTURA": str,
    "NFACTURA": str,
    "NUMTRASP": str,
    "VALORCOM": str,
    "VENGAS": str,
    "VENRT": str,
    "FECHART": str,
    "FECHAGAS": str,
    "DESTRASP": str,
    "CAPACIDAD_M3": str,
    "CAPACIDAD_PAX": str,
    "CAPACIDAD_TON": str,
    "MFACTREMATE": str,
    "IMAGEN": str,
    "UFECHA": str,
}

# Atributos de los activos
rnm_df = pd.read_csv(
    "../../data/external/asset_vehiculosv2.csv", sep=";", dtype=dtype_dic_rnm
)

# Añadir tipología (CLASE), ubicación (LOCATION), año adquisición (YEAR), última lectura del medidor (ulectura)
data_resampled = pd.merge(
    left=data_resampled,
    right=rnm_df[["ASSETNUM", "CLASE", "LOCATION", "AÑO", "ULECTURA"]],
    how="left",
    left_on="activo",
    right_on="ASSETNUM",
)

# Borrar columna repetida
del data_resampled["ASSETNUM"]

# Renombrar columnas
data_resampled.columns = [
    "FECHA",
    "activo",
    "sigla",
    "medidor",
    "ini",
    "fin",
    "region",
    "bit-year",
    "set",
    "delta",
    "type",
    "loc",
    "year",
    "ulectura",
]

# Eliminar NA de las columnas type y ulectura
data_resampled = data_resampled.dropna(subset=["type", "ulectura"])

# Eliminar equipos SIN MEDIDOR
data_resampled = data_resampled[data_resampled["ulectura"] != "SIN MEDIDOR"]

# Reindexar FECHA
data_resampled["FECHA"] = pd.to_datetime(data_resampled["FECHA"])
data_resampled = data_resampled.set_index("FECHA")

# Tipo de data
data_resampled["set"] = data_resampled["set"].astype("int")
data_resampled["ulectura"] = data_resampled["ulectura"].apply(
    lambda x: float(str(x).replace(".", "").replace(",", ".")) if pd.notna(x) else None
)

# Ordenar columnas
data_resampled = data_resampled[
    [
        "activo",
        "sigla",
        "medidor",
        "ini",
        "fin",
        "region",
        "bit-year",
        "set",
        "type",
        "loc",
        "year",
        "ulectura",
        "delta",
    ]
]

# Revisión
data_resampled.info()

# --------------------------------------------------------------
# Exportar dataset
# --------------------------------------------------------------
data_resampled.to_pickle("../../data/interim/01_data_processed.pkl")
data_resampled.to_csv("../../data/interim/01_data_processed.csv")
