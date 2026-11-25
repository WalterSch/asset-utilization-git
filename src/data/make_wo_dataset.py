# Libraries
import pandas as pd
from datetime import datetime

# --------------------------------------------------------------
# OT dataset
# --------------------------------------------------------------

# Diccionario OT Orden de Trabajo CONTRATO
dtype_dic_otext = {
    'REPORTEDBY': str,
    'WONUM': str,
    'ASSETNUM': str,
    'SIGLA': str,
    'LOCATION': str,
    'REPORTDATE': str,
    'STATUS': str,
    'CONTRATOMAQ': str,
    'DESCRPTION': str,
    'UBICACION': str,
    'PONUM': str,
    'STATUS2': str,
    'RECEIPTS': str,
    'COSTO': float,
    'INACTIVIDAD': str,
    'BITACORA': str,
    'REMARKS': str,
    'WORKTYPE': str,
    'COTIZACION': str,
    'FECHACOT': str,
    'RESOLCOMP': str,
    'FECHARESOL': str,
    'APROBADO': str,
    'OCPORTAL': str,
    'FECHAOC': str,
    'NUMFACT': str,
    'FECHAFAC': str,
    'description': str,
    'DOWNTIME': float}

# Diccionario OT Orden de Trabajo TRATO DIRECTO
dtype_dic_ottd = {
    'REPORTEDBY': str,
    'WONUM': str,
    'ASSETNUM': str,
    'SIGLA': str,
    'LOCATION': str,
    'REPORTDATE_1': str,
    'STATUS': str,
    'PONUM': str,
    'STATUS2': str,
    'RECEIPTS': str,
    'COSTO_1': float,
    'INACTIVIDAD': str,
    'BITACORA': str,
    'REMARKS': str,
    'OCPORTAL': str,
    'FECHAOC': str,
    'DOWNTIME': float}

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
ot_ext_df = pd.read_csv("../../data/external/estadoOTmaquinarias.csv", sep=";", dtype=dtype_dic_otext)
ot_td_df = pd.read_csv("../../data/external/estadoOTmaquinariasTD.csv", sep=";", dtype=dtype_dic_ottd)

# --------------------------------------------------------------
# Estructurar data
# --------------------------------------------------------------

# Eliminar filas que contienen Nan en SIGLA  y UBICACION
ot_ext_df = ot_ext_df.dropna(subset=['SIGLA','UBICACION'])
# Eliminar OT CANCELADAS
ot_ext_df = ot_ext_df[(ot_ext_df['STATUS'] != 'CAN') & (ot_ext_df['STATUS'] != 'CANCEL')]

# Tratamiento de fechas
ot_td_df['REPORTDATE_1'] = pd.to_datetime(ot_td_df['REPORTDATE_1'])
# Tipo de trabajo
ot_td_df['WORKTYPE'] = "MC"
# Renombrar columnas
ot_td_df = ot_td_df.rename(
    columns={
        "REPORTDATE_1": "REPORTDATE",
        "COSTO_1": "COSTO"})

# Eliminar filas que contienen Nan en SIGLA  y UBICACION
ot_td_df = ot_td_df.dropna(subset=['SIGLA','LOCATION'])
# Eliminar OT CANCELADAS
ot_td_df = ot_td_df[(ot_td_df['STATUS'] != 'CAN') & (ot_td_df['STATUS'] != 'CANCEL')]

# --------------------------------------------------------------
# Elementos duplicados
# --------------------------------------------------------------

# Tratamiento OT duplicadas
dupl = ot_ext_df[ot_ext_df['WONUM'].duplicated()]["WONUM"].unique()
# Lista de OT's no duplicadas
lista = []
# Lista de OT duplicadas en donde ambas OT tiene Recepción COMPLETA en EEPP
lista_dupl = []
# Lista de OT duplicadas en donde ninguna OT tiene Recepción COMPLETA en EEPP
lista_dupl_s_receipt = []
for ot in dupl:
    # Subset solo con ot duplicada
    subset = ot_ext_df[ot_ext_df['WONUM'] == ot]
    # Subset con ot (o ots) con Recepción COMPLETA
    subset_receipt_compl = subset[subset["RECEIPTS"] == 'COMPLETA']
    # Numero de OT en subset_receipt_compl
    num_filas = len(subset_receipt_compl)
    # Si ninguna OT tiene recepción COMPLETA, se escoge el primer elemento
    if subset_receipt_compl.empty:
        fila = subset.iloc[0]
        lista_dupl_s_receipt.append(subset)
    # Si hay más de una OT con recepción COMPLETA, se escoge el primer elemento
    elif num_filas > 1:
        fila = subset_receipt_compl.iloc[0]
        lista_dupl.append(subset_receipt_compl)
    # Si hay una OT con recepción completa, que se escoja esa OT
    else:
        fila = subset_receipt_compl.iloc[0]
    lista.append(fila)

# DataFrame con OT únicas
df = pd.DataFrame(lista)
# OT's duplicadas, ambas con Recepción COMPLETA
df_dupl = pd.concat(lista_dupl, ignore_index = True)
# OT's duplicadas, ninguna con Recepción COMPLETA
df_dupl_s_receipt = pd.concat(lista_dupl_s_receipt, ignore_index = True)

# Eliminar OT's duplicadas
ot_ext_df = ot_ext_df[~ot_ext_df["WONUM"].isin(dupl)]

# Concatenar con lista única de ot's duplicadas "df"
ot_ext_df = pd.concat([ot_ext_df, df], ignore_index=True)

# --------------------------------------------------------------
# Tratamiento de Fechas
# --------------------------------------------------------------

# Funcion para tratamiento de fechas
def parse_fecha(fecha_str):
    try:
        return datetime.strptime(fecha_str, '%d-%m-%Y')
    except:
        return pd.NaT
    
# Reemplazar mes
ot_ext_df['REPORTDATE'] = ot_ext_df['REPORTDATE'].replace(meses, regex=True)
# Eliminar ","
ot_ext_df['REPORTDATE'] = ot_ext_df['REPORTDATE'].str.replace(',', '', regex=False)
# Llevar formato datetime
ot_ext_df['REPORTDATE'] = pd.to_datetime(ot_ext_df['REPORTDATE'],format="%m %d %Y", errors='coerce')
# Transformar a fecha
ot_ext_df['FECHACOT'] = ot_ext_df['FECHACOT'].apply(parse_fecha)
ot_ext_df['FECHARESOL'] = ot_ext_df['FECHARESOL'].apply(parse_fecha)
ot_ext_df['FECHAOC'] = ot_ext_df['FECHAOC'].apply(parse_fecha)
ot_ext_df['FECHAFAC'] = ot_ext_df['FECHAFAC'].apply(parse_fecha)

# Calcular antiguedad OT
hoy = pd.to_datetime(datetime.today())
ot_ext_df['Antiguedad_Años'] = (hoy - ot_ext_df['REPORTDATE']).dt.days // 365
ot_ext_df['Antiguedad_Días'] = (hoy - ot_ext_df['REPORTDATE']).dt.days


# Filtrar y Reordenar
ot_ext_df = ot_ext_df[['REPORTEDBY', 'WONUM', 'ASSETNUM', 'SIGLA', 'LOCATION', 'REPORTDATE',
       'STATUS', 'PONUM', 'STATUS2',
       'RECEIPTS', 'COSTO', 'INACTIVIDAD', 'BITACORA', 'REMARKS',
       'OCPORTAL', 'FECHAOC', 'DOWNTIME', 'WORKTYPE']]

ot_df = pd.concat([ot_ext_df, ot_td_df],ignore_index=True)

# --------------------------------------------------------------
# Exportar datos
# --------------------------------------------------------------
ot_df.to_pickle('../../reports/OTmaquinarias.pkl')

ot_df.to_excel('../../reports/estadoOTmaquinarias.xlsx')
df_dupl.to_excel('../../reports/estadoOTmaquinarias_dupl_rec_COMPLETA.xlsx')
df_dupl_s_receipt.to_excel('../../reports/estadoOTmaquinarias_dupl_rec_NINGUNA.xlsx')
