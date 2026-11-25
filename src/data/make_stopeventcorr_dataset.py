# Libraries
import pandas as pd

# --------------------------------------------------------------
# Carga de datos
# --------------------------------------------------------------

ot_dt_df = pd.read_pickle("../../reports/OTmaquinariasMCKMeans.pkl")
ot_dt_df = ot_dt_df.dropna()
ot_dt_df = ot_dt_df.reset_index()

ot_bit_df = pd.read_pickle("../../reports/OTmaquinariasStopEvent.pkl")
ot_bit_df = ot_bit_df.reset_index()


# OT MC solamente
mc_df = ot_dt_df.sort_values(["SIGLA", "REPORTDATE"])
bit_df = ot_bit_df.sort_values(["SIGLA", "REPORTDATE"])

# siguiente detención
bit_df["FECHA_FIN"] = bit_df.groupby("SIGLA")["REPORTDATE"].shift(-1)

res = pd.merge(mc_df, bit_df[["SIGLA", "REPORTDATE", "FECHA_FIN"]], on="SIGLA")

res = res[
    (res["REPORTDATE_x"] >= res["REPORTDATE_y"])
    & (res["FECHA_FIN"].isna() | (res["REPORTDATE_x"] < res["FECHA_FIN"]))
]

idx_mc = res[["SIGLA", "REPORTDATE_y"]].drop_duplicates().assign(CLASIFICACION="MC")

ot_bit_df = ot_bit_df.merge(
    idx_mc,
    left_on=["SIGLA", "REPORTDATE"],
    right_on=["SIGLA", "REPORTDATE_y"],
    how="left",
)

ot_bit_df["CLASIFICACION"] = ot_bit_df["CLASIFICACION"].fillna("OTRA")

idx_mc = idx_mc.rename(columns={"REPORTDATE_y": "REPORTDATE"})
del idx_mc["CLASIFICACION"]
idx_mc["COSTO"] = 0
idx_mc["WONUM"] = 0

idx_mc.to_pickle("../../reports/OTmaquinariasStopEventcorr.pkl")
