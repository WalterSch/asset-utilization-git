import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from IPython.display import display

# --------------------------------------------------------------
# Load data
# --------------------------------------------------------------
df = pd.read_pickle("../../data/interim/01_data_processed.pkl")

# --------------------------------------------------------------
# Plot single asset
# --------------------------------------------------------------
set_df = df[df["sigla"] == "10U-MMVO-363"]

# time; how long a set is?
plt.plot(set_df["delta"])

# number of samples; how many samples are in there?
plt.plot(set_df["delta"].reset_index(drop=True))

# by month
sampling = {
    'sigla': "last",
    'medidor': "last",
    'ini': "first",
    'fin': "last",
    'region': "last",
    'bit-year': "last",
    'set': "last",
    'type': "last",
    'loc': "last",
    'year': "last",
    'ulectura': "last",
    'delta': "sum"}

# resamplig
df_resampled = (
    set_df.groupby([pd.Grouper(freq="ME"), "activo"])
    .agg(sampling)
    .dropna()
    .reset_index()
)

df_resampled = df_resampled[(df_resampled['FECHA'] >= '2024-01-01') & (df_resampled['FECHA'] <= '2024-12-31')]
df_resampled = df_resampled.set_index("FECHA")
plt.plot(df_resampled["delta"])
df_resampled["delta"].sum()

# --------------------------------------------------------------
# Plot all
# --------------------------------------------------------------
# time
for desc in df["type"].unique():
    subset = df[df["type"] == desc]
    df_resampled = (
        subset.groupby([pd.Grouper(freq="ME"), "activo"])
        .agg(sampling)
        .dropna()
        .reset_index()
    )
    
    df_resampled = df_resampled.set_index("FECHA")
    
    fig, ax = plt.subplots()
    plt.plot(df_resampled["delta"], label=desc)
    plt.legend()
    plt.show()

# number of samples, min/max values
for desc in df["type"].unique():
    subset = df[df["type"] == desc]
    df_resampled = (
        subset.groupby([pd.Grouper(freq="ME"), "activo"])
        .agg(sampling)
        .dropna()
        .reset_index()
    )
    
    df_resampled = df_resampled.sort_values(by="delta").reset_index()
    
    fig, ax = plt.subplots()
    plt.plot(df_resampled["delta"], label=desc)
    plt.legend()
    plt.show()

print(f"{len(df["year"].unique())} distinct years")
print(f"{len(df["type"].unique())} distinct types")
print(f"{len(df["loc"].unique())} distinct locations")

# --------------------------------------------------------------
# Adjust plot settings
# --------------------------------------------------------------
mpl.style.use("seaborn-v0_8-deep")
mpl.rcParams["figure.figsize"] = (20, 5)
mpl.rcParams["figure.dpi"] = 100

# --------------------------------------------------------------
# Compare locations
# --------------------------------------------------------------
asset_df = df.query("type == 'MOTONIVELADORA'").query("region == '04'")
df_resampled = (asset_df.groupby([pd.Grouper(freq="ME"), "activo"]).agg(sampling).dropna().reset_index())
df_resampled = df_resampled.sort_values(by=["loc", "delta"]).reset_index()

fig, ax = plt.subplots()
df_resampled.groupby(["loc"])["delta"].plot()
ax.set_ylabel("delta")
ax.set_xlabel("samples")
plt.legend()
plt.title("Uso Mensual - location - MOTONIVELADORA - 04")
plt.show()

# --------------------------------------------------------------
# Compare types
# --------------------------------------------------------------
type_df = df.query("medidor == 'HOROMET'").query("region == '12'")
df_resampled = (type_df.groupby([pd.Grouper(freq="ME"), "activo"]).agg(sampling).dropna().reset_index())
df_resampled = df_resampled.sort_values(by=["type", "delta"]).reset_index()

fig, ax = plt.subplots()
df_resampled.groupby(["type"])["delta"].plot()
ax.set_ylabel("delta")
ax.set_xlabel("samples")
plt.legend()
plt.title("Uso Mensual - type - HOROMET - 12")
plt.show()

# --------------------------------------------------------------
# Compare years
# --------------------------------------------------------------
year_df = df.query("type == 'MOTONIVELADORA'").query("region == '14'")
df_resampled = (year_df.groupby([pd.Grouper(freq="ME"), "activo"]).agg(sampling).dropna().reset_index())
df_resampled = df_resampled.sort_values(by=["year", "delta"]).reset_index()

fig, ax = plt.subplots()
df_resampled.groupby(["year"])["delta"].plot()
ax.set_ylabel("delta")
ax.set_xlabel("samples")
plt.legend()
plt.title("Uso Mensual - year - MOTONIVELADORA - 14")
plt.show()

# --------------------------------------------------------------
# Compare ulectura
# --------------------------------------------------------------
ulectura_df = df.query("type == 'MOTONIVELADORA'").query("region == '12'")
df_resampled = (ulectura_df.groupby([pd.Grouper(freq="ME"), "activo"]).agg(sampling).dropna().reset_index())
df_resampled = df_resampled.sort_values(by=["ulectura", "delta"]).reset_index()

fig, ax = plt.subplots()
df_resampled.groupby(["ulectura"])["delta"].plot()
ax.set_ylabel("delta")
ax.set_xlabel("samples")
plt.legend()
plt.title("Uso Mensual - ulectura - MOTONIVELADORA - 12")
plt.show()

# --------------------------------------------------------------
# Compare bit-year
# --------------------------------------------------------------
bit_year_df = df.query("type == 'CAMION TOLVA'").query("region == '11'")
df_resampled = (bit_year_df.groupby([pd.Grouper(freq="ME"), "activo"]).agg(sampling).dropna().reset_index())
df_resampled = df_resampled.sort_values(by=["bit-year", "delta"]).reset_index()

fig, ax = plt.subplots()
df_resampled.groupby(["bit-year"])["delta"].plot()
ax.set_ylabel("delta")
ax.set_xlabel("samples")
plt.legend()
plt.title("Uso Mensual - bityear - CAMION TOLVA - 11")
plt.show()

# --------------------------------------------------------------
# Plot multiple axis
# --------------------------------------------------------------
desc = "MOTONIVELADORA"
region = "04"

all_axis_df = df.query(f"type == '{desc}'").query(f"region == '{region}'")
df_resampled = (all_axis_df.groupby([pd.Grouper(freq="ME"), "activo"]).agg(sampling).dropna().reset_index())
df_resampled = df_resampled.sort_values(by=["ulectura", "delta"]).reset_index()

# in one figure
fig, ax = plt.subplots()
df_resampled[["delta", "ulectura"]].plot(ax=ax)
ax.set_ylabel("delta")
ax.set_xlabel("samples")
plt.legend()
plt.show()

# in two figures
fig, ax = plt.subplots(nrows=2, sharex=True, figsize=(20, 10))
df_resampled[["delta"]].plot(ax=ax[0])
df_resampled[["ulectura"]].plot(ax=ax[1])

ax[0].legend(
    loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=3, fancybox=True, shadow=True
)
ax[1].legend(
    loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=3, fancybox=True, shadow=True
)
ax[1].set_xlabel("samples")

plt.savefig(f"../../reports/figures/{desc.title()} ({region}).png")
plt.show()

# --------------------------------------------------------------
# Loop over all combinations and export
# --------------------------------------------------------------
types = df["type"].unique()
regions = df["region"].unique()

for desc in types:
    for region in regions:
        combined_plot_df = (
            df.query(f"type == '{desc}'").query(f"region == '{region}'")
        )
        
        df_resampled = (combined_plot_df.groupby([pd.Grouper(freq="ME"), "activo"]).agg(sampling).dropna().reset_index())
        df_resampled = df_resampled.sort_values(by=["ulectura", "delta"]).reset_index()

        if len(combined_plot_df) > 0:
            
            fig, ax = plt.subplots(nrows=2, sharex=True, figsize=(20, 10))
            df_resampled[["delta"]].plot(ax=ax[0])
            df_resampled[["ulectura"]].plot(ax=ax[1])

            ax[0].legend(
                loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=3, fancybox=True, shadow=True
            )
            ax[1].legend(
                loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=3, fancybox=True, shadow=True
            )
            ax[1].set_xlabel("samples")
            
            plt.savefig(f"../../reports/figures/{desc.title()} ({region}).png")
            
            plt.show()
