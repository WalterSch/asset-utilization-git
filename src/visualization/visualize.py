import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from IPython.display import display

# --------------------------------------------------------------
# Load data
# --------------------------------------------------------------
df = pd.read_pickle("../../data/interim/01_data_processed.pkl")

# --------------------------------------------------------------
# Plot single columns
# --------------------------------------------------------------
set_df = df[df["sigla"] == "10U-MMVO-363"]

# time; how long a set is?
plt.plot(set_df["delta"])

# number of samples; how many samples are in there?
plt.plot(set_df["delta"].reset_index(drop=True))

# month
sampling = {
    "sigla": "last",
    "medidor": "last",
    "ini": "first",
    "fin": "last",
    "region": "last",
    "bit-year": "last",
    "set": "last",
    "type": "last",
    "loc": "last",
    "year": "last",
    "ulectura": "last",
    "delta": "sum",
}

df_resampled = (
    set_df.groupby([pd.Grouper(freq="MS"), "activo"])
    .agg(sampling)
    .dropna()
    .reset_index()
)


df_resampled = df_resampled[
    (df_resampled["FECHA"] >= "2024-01-01") & (df_resampled["FECHA"] <= "2024-12-31")
]
df_resampled = df_resampled.set_index("FECHA")
plt.plot(df_resampled["delta"])
df_resampled["delta"].sum()
# --------------------------------------------------------------
# Plot all
# --------------------------------------------------------------
# delta through time
for desc in df["type"].unique():
    subset = df[df["type"] == desc]
    fig, ax = plt.subplots()
    plt.plot(subset["delta"].reset_index(drop=True), label=desc)
    plt.legend()
    plt.show()

# sorted delta
for desc in df["type"].unique():
    subset = df[df["type"] == desc]
    subset = subset.sort_values(by="delta")
    fig, ax = plt.subplots()
    plt.plot(subset["delta"].reset_index(drop=True), label=desc)
    plt.legend()
    plt.show()

print(f"{len(df['year'].unique())} distinct years")
print(f"{len(df['type'].unique())} distinct types")
print(f"{len(df['loc'].unique())} distinct locations")

# --------------------------------------------------------------
# Adjust plot settings
# --------------------------------------------------------------
mpl.style.use("seaborn-v0_8-deep")
mpl.rcParams["figure.figsize"] = (20, 5)
mpl.rcParams["figure.dpi"] = 100

# --------------------------------------------------------------
# Compare locations
# --------------------------------------------------------------
asset_df = (
    df.query("type == 'MOTONIVELADORA'")
    .query("region == '04'")
    .sort_values(by="loc")
    .reset_index()
)

fig, ax = plt.subplots()
asset_df.groupby(["loc"])["delta"].plot()
ax.set_ylabel("delta")
ax.set_xlabel("samples")
plt.legend()
plt.show()


# --------------------------------------------------------------
# Compare types
# --------------------------------------------------------------
type_df = (
    df.query("medidor == 'HOROMET'")
    .query("region == '12'")
    .sort_values(by="type")
    .reset_index()
)

fig, ax = plt.subplots()
type_df.groupby(["type"])["delta"].plot()
ax.set_ylabel("delta")
ax.set_xlabel("samples")
plt.legend()
plt.show()

# --------------------------------------------------------------
# Compare years
# --------------------------------------------------------------
year_df = (
    df.query("type == 'MOTONIVELADORA'")
    .query("region == '14'")
    .sort_values(by="year")
    .reset_index()
)

fig, ax = plt.subplots()
year_df.groupby(["year"])["delta"].plot()
ax.set_ylabel("delta")
ax.set_xlabel("samples")
plt.legend()
plt.show()

# --------------------------------------------------------------
# Compare ulectura
# --------------------------------------------------------------
ulectura_df = (
    df.query("type == 'MOTONIVELADORA'")
    .query("region == '12'")
    .sort_values(by="ulectura")
    .reset_index()
)

fig, ax = plt.subplots()
ulectura_df.groupby(["ulectura"])["delta"].plot()
ax.set_ylabel("delta")
ax.set_xlabel("samples")
plt.legend()
plt.show()

# --------------------------------------------------------------
# Compare bit-year
# --------------------------------------------------------------
bit_year_df = (
    df.query("type == 'CAMION TOLVA'")
    .query("region == '11'")
    .sort_values(by="bit-year")
    .reset_index()
)

fig, ax = plt.subplots()
bit_year_df.groupby(["bit-year"])["delta"].plot()
ax.set_ylabel("delta")
ax.set_xlabel("samples")
plt.legend()
plt.show()

# --------------------------------------------------------------
# Plot multiple axis
# --------------------------------------------------------------
desc = "CAMION ALJIBE"
region = "04"

all_axis_df = (
    df.query(f"type == '{desc}'")
    .query(f"region == '{region}'")
    .sort_values(by="ulectura")
    .reset_index()
)

# in one figure
fig, ax = plt.subplots()
all_axis_df[["delta", "ulectura"]].plot(ax=ax)
ax.set_ylabel("delta")
ax.set_xlabel("samples")
plt.legend()
plt.show()

# in two figures
fig, ax = plt.subplots(nrows=2, sharex=True, figsize=(20, 10))
all_axis_df[["delta"]].plot(ax=ax[0])
all_axis_df[["ulectura"]].plot(ax=ax[1])

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
            df.query(f"type == '{desc}'")
            .query(f"region == '{region}'")
            .sort_values(by="ulectura")
            .reset_index()
        )

        if len(combined_plot_df) > 0:
            fig, ax = plt.subplots(nrows=2, sharex=True, figsize=(20, 10))
            combined_plot_df[["delta"]].plot(ax=ax[0])
            combined_plot_df[["ulectura"]].plot(ax=ax[1])

            ax[0].legend(
                loc="upper center",
                bbox_to_anchor=(0.5, 1.15),
                ncol=3,
                fancybox=True,
                shadow=True,
            )
            ax[1].legend(
                loc="upper center",
                bbox_to_anchor=(0.5, 1.15),
                ncol=3,
                fancybox=True,
                shadow=True,
            )
            ax[1].set_xlabel("samples")

            plt.show()
