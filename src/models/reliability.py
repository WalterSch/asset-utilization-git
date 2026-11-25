# Libraries
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from scipy.stats import weibull_min
from scipy.special import gamma

# --------------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------------

print("Cargando datasets...")

bit_df = pd.read_pickle("../../data/interim/02_outliers_removed_chauvenets.pkl")

bit_df = bit_df.dropna()
bit_df.info()

ot_df = pd.read_pickle("../../reports/OTmaquinariasStopEventcorr.pkl")
ot_df.info()

bit_df = bit_df.reset_index()
ot_df = ot_df.reset_index()

# Reliability
# Mayores registros
bit_df.groupby("sigla")["delta"].count().reset_index().sort_values(
    "delta", ascending=False
).head(30)
# Asset
sigla = "3C-CAFR-1068"

asset_ot_df = ot_df[ot_df["SIGLA"] == sigla]

fecha_min = min(asset_ot_df["REPORTDATE"])
fecha_max = max(asset_ot_df["REPORTDATE"])

asset_bit_df = bit_df[
    (bit_df["sigla"] == sigla)
    & (bit_df["FECHA"] >= fecha_min)
    & (bit_df["FECHA"] <= fecha_max)
]


# ploting two figures
asset_ot_df = asset_ot_df.sort_values("REPORTDATE")
asset_bit_df = asset_bit_df.sort_values("FECHA")

asset_ot_df.index = asset_ot_df["REPORTDATE"]
asset_bit_df.index = asset_bit_df["FECHA"]
fig, ax = plt.subplots(nrows=2, sharex=True, figsize=(20, 10))
asset_ot_df["COSTO"].plot(ax=ax[0], marker="o", markersize=5)
asset_bit_df["delta"].plot(ax=ax[1])

# Líneas verticales en cada OT
for fecha in asset_ot_df.index:
    ax[0].axvline(fecha, color="red", linestyle="--", alpha=0.5)
    ax[1].axvline(fecha, color="red", linestyle="--", alpha=0.5)

ax[0].legend(
    loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=3, fancybox=True, shadow=True
)
ax[1].legend(
    loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=3, fancybox=True, shadow=True
)
ax[1].set_xlabel("samples")

plt.show()

# time to failure
asset_bit_df = asset_bit_df.reset_index(drop=True)
asset_ot_df = asset_ot_df.reset_index(drop=True)

asset_bit_df = asset_bit_df.sort_values("FECHA")
asset_ot_df = asset_ot_df.sort_values("REPORTDATE")

# Dataframe resultado
tbf_df = pd.DataFrame()

# Fecha inicial
fecha_ini = asset_bit_df["FECHA"].min()

for _, ot in asset_ot_df.iterrows():
    fecha_fin = ot["REPORTDATE"]

    tiempo_falla = asset_bit_df.loc[
        (asset_bit_df["FECHA"] >= fecha_ini) & (asset_bit_df["FECHA"] < fecha_fin),
        "delta",
    ].sum()

    fila = pd.DataFrame(
        {
            "SIGLA": [ot["SIGLA"]],
            "WONUM": [ot["WONUM"]],
            "FECHA_FALLA": [fecha_fin],
            "TBF": [tiempo_falla],
        }
    )

    tbf_df = pd.concat([tbf_df, fila], ignore_index=True)

    # La próxima ventana comienza en esta falla
    fecha_ini = fecha_fin

tbf_df = tbf_df[tbf_df["TBF"] > 0]

# Boxplot
tbf_df.boxplot(column="TBF", by="SIGLA", figsize=(20, 8))
plt.xticks(rotation=90)
plt.show()

# Hist
tbf_df["TBF"].plot.hist(figsize=(20, 8))
plt.show()

""" Weibull """
tbf = tbf_df["TBF"].dropna()
tbf = tbf[tbf > 0]

shape, loc, scale = weibull_min.fit(tbf, floc=0)

beta = shape
eta = scale

if beta < 0.9:
    comment = "Mortalidad infantil"
elif beta >= 0.9 and beta <= 1.1:
    comment = "Fallas aleatorias"
else:
    comment = "Desgaste"

print(f"Beta: {beta}, {comment}")
print(f"Eta: {eta}")

x = np.linspace(0, tbf.max() * 1.2, 1000)

pdf = weibull_min.pdf(x, beta, loc=0, scale=eta)

# plot
plt.figure(figsize=(10, 5))
plt.hist(tbf, bins=20, density=True, alpha=0.5, label="TBF Observado")
plt.plot(x, pdf, color="red", linewidth=2, label="Weibull Ajustada")
plt.xlabel("Horas / Km entre Fallas")
plt.ylabel("Densidad")
plt.legend()
plt.show()


r100 = 1 - weibull_min.cdf(100, beta, loc=0, scale=eta)
r5000 = 1 - weibull_min.cdf(5000, beta, loc=0, scale=eta)
print(f"Confiabilidad a las 100 [hrs] {r100}")
print(f"Confiabilidad a las 5000 [kms] {r5000}")

# curva de confiabilidad
r = 1 - weibull_min.cdf(x, beta, scale=eta)

plt.figure(figsize=(10, 5))
plt.plot(x, r, linewidth=2)
plt.xlabel("Horas/Km")
plt.ylabel("Confiabilidad")
plt.title("R(t)")
plt.grid()
plt.show()

# MTBF
mtbf = tbf.mean()
mtbf_weibull = eta * gamma(1 + 1 / beta)

print(f"Empírico: {mtbf}")
print(f"Weibull: {mtbf_weibull}")
