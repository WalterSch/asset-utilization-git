# Libraries
import pandas as pd
import matplotlib.pyplot as plt

# K-means
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# --------------------------------------------------------------
# OT dataset
# --------------------------------------------------------------

ot_df = pd.read_pickle("../../reports/OTmaquinarias.pkl")
ot_df["REPORTDATE"] = pd.to_datetime(ot_df["REPORTDATE"])
ot_df = ot_df.set_index("REPORTDATE")
ot_df.info()

# --------------------------------------------------------------
# K-means: determinar número de clusters
# --------------------------------------------------------------

# Variables para clustering
X = ot_df[['COSTO','DOWNTIME']].fillna(0)

# Escalamiento
# K-Means utiliza distancia euclidiana, por lo que es necesario
# escalar las variables para que ambas tengan igual importancia
# independientemente de sus unidades o magnitudes
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Lista donde se almacenará la inercia calculada para cada K
inertia = []

# Se evaluarán entre 1 y 20 clusters
K = range(1, 21)

for k in K:
    print(f"probando con {k} clusters")
    
    # Entrenamiento del modelo para cada valor de K
    kmeans = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=20
    )

    kmeans.fit(X_scaled)
    
    # La inercia corresponde a la suma de las distancias
    # cuadráticas de cada punto a su centroide
    inertia.append(
        kmeans.inertia_
    )

# Visualización del método del codo para determinar el número adecuado de clusters
plt.figure(figsize=(8,5))
plt.plot(K, inertia, marker="o")
plt.xlabel("Número de Clusters")
plt.ylabel("Inercia")
plt.title("Método del Codo")
plt.show()

# --------------------------------------------------------------
# Entrenamiento final de K-Means
# --------------------------------------------------------------

# Se utiliza el número de clusters definido a partir del análisis anterior
kmeans = KMeans(
    n_clusters=20,
    random_state=42,
    n_init=20
)

# Asignación del cluster correspondiente a cada OT
ot_df["Cluster"] = kmeans.fit_predict(X_scaled)

# Obtención de los valores promedio de costo y tiempo fuera de servicio para cada cluster
resumen = (ot_df.groupby("Cluster")[['COSTO','DOWNTIME']].mean().reset_index())
print(resumen)

# --------------------------------------------------------------
# Selección de clusters asociados a mantenimiento correctivo
# --------------------------------------------------------------

# Se utilizan percentiles para definir umbrales altos de costo y tiempo fuera de servicio
cost_threshold = ot_df["COSTO"].quantile(0.55)
downtime_threshold = ot_df["DOWNTIME"].quantile(0.55)

# Funcion matematica por columna
sampling = {
    "COSTO": "mean",
    "DOWNTIME": "mean"}

# Resumen estadístico por cluster
cluster_summary = (ot_df.groupby("Cluster").agg(sampling))

# Lista de clusters cuyo costo promedio y downtime promedio superan simultáneamente ambos umbrales
corrective_clusters = cluster_summary[
    (cluster_summary["COSTO"] >= cost_threshold)
    &
    (cluster_summary["DOWNTIME"] >= downtime_threshold)
].index.tolist()

print(corrective_clusters)

# --------------------------------------------------------------
# Extracción de OT de mantenimiento correctivo
# --------------------------------------------------------------

mc_ot_df = ot_df[ot_df["Cluster"].isin(corrective_clusters)]

mc_ot_df.to_pickle('../../reports/OTmaquinariasMCKMeans.pkl')
