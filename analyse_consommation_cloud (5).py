

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------------
# 1. COLLECTE / GENERATION DES DONNEES
# -------------------------------------------------------------
np.random.seed(42)

n_rows = 800
resource_ids = [f"RES-{i:05d}" for i in range(1, n_rows + 1)]
regions = ["Us-East-1", "Eu-West-1", "Ap-South-1", "Us-West-2"]
providers = ["AWS", "Azure", "Google Cloud"]
statuses = ["Active", "Stopped", "Running", "Deleted", "Terminated", "Error"]
resource_types = ["Virtual Machine", "Storage", "Database", "Network"]

dates = pd.date_range("2024-01-01", periods=24, freq="MS")  # 24 mois

data = {
    "Resource_ID": resource_ids,
    "Region": np.random.choice(regions, n_rows),
    "Cloud_Provider": np.random.choice(providers, n_rows),
    "Resource_Status": np.random.choice(statuses, n_rows, p=[0.30, 0.22, 0.22, 0.12, 0.09, 0.05]),
    "Resource_Type": np.random.choice(resource_types, n_rows, p=[0.45, 0.25, 0.20, 0.10]),
    "Creation_Date": np.random.choice(dates, n_rows),
    "Hourly_Cost": np.round(np.random.gamma(shape=2.0, scale=0.9, size=n_rows), 2),
    "CPU_Utilization_Pct": np.round(np.random.beta(1.5, 3, n_rows) * 100, 1),
}

df = pd.DataFrame(data)

# Introduction volontaire d'anomalies réalistes (pour illustrer le nettoyage)
df.loc[df.sample(frac=0.02, random_state=1).index, "Hourly_Cost"] *= -1        # coûts négatifs
df.loc[df.sample(frac=0.015, random_state=2).index, "CPU_Utilization_Pct"] = 135  # % impossible
df.loc[df.sample(frac=0.01, random_state=3).index, "Hourly_Cost"] = np.nan     # valeurs manquantes

print("Aperçu brut du jeu de données :")
print(df.head())
print("\nDimensions :", df.shape)

# -------------------------------------------------------------
# 2. NETTOYAGE ET PREPARATION
# -------------------------------------------------------------
# Coûts manquants -> imputés par la médiane (plutôt que suppression, pour préserver le volume)
df["Hourly_Cost"] = df["Hourly_Cost"].fillna(df["Hourly_Cost"].median())

# Coûts négatifs -> valeur absolue (erreur de saisie probable)
df["Hourly_Cost"] = df["Hourly_Cost"].abs()

# Taux d'utilisation impossibles (> 100 %) -> écrêtage à 100
df.loc[df["CPU_Utilization_Pct"] > 100, "CPU_Utilization_Pct"] = 100

# Conversion des types
df["Creation_Date"] = pd.to_datetime(df["Creation_Date"])
df["Mois"] = df["Creation_Date"].dt.strftime("%Y-%m")

print("\nAprès nettoyage :", df.shape)
print(df.describe(include=[np.number]))

# -------------------------------------------------------------
# 3. ANALYSE EXPLORATOIRE (EDA)
# -------------------------------------------------------------
# Dépense mensuelle projetée (mois cloud standard = 730 heures)
df["Projected_Monthly_Spend"] = df["Hourly_Cost"] * 730

cout_par_provider = df.groupby("Cloud_Provider")["Projected_Monthly_Spend"].sum().sort_values(ascending=False)
print("\nDépense mensuelle projetée par fournisseur :\n", cout_par_provider)

evolution_mensuelle = df.groupby("Mois")["Projected_Monthly_Spend"].sum().sort_index()
print("\nÉvolution mensuelle des coûts :\n", evolution_mensuelle.tail())

# -------------------------------------------------------------
# 3bis. DETECTION DES RESSOURCES "ZOMBIES"
# -------------------------------------------------------------
# Ressource "zombie" : coûte cher (> 1,50 $/h) mais utilisée à moins de 15 % de CPU
# (indicateur inspiré de pratiques FinOps réelles de détection de gaspillage)
seuil_cout = 1.5
seuil_cpu = 15

zombies = df[(df["Hourly_Cost"] > seuil_cout) & (df["CPU_Utilization_Pct"] < seuil_cpu)]
economies_potentielles = zombies["Projected_Monthly_Spend"].sum()

print(f"\nNombre de ressources 'zombies' détectées : {len(zombies)}")
print(f"Économies mensuelles potentielles si arrêtées : {economies_potentielles:,.2f} €")
print(f"Part du budget total concernée : {economies_potentielles / df['Projected_Monthly_Spend'].sum() * 100:.1f} %")

# -------------------------------------------------------------
# 4. VISUALISATIONS (Figures du Chapitre 4)
# -------------------------------------------------------------

# Figure 6 : Répartition des coûts par fournisseur cloud
fig1, ax1 = plt.subplots(figsize=(6, 5))
ax1.pie(cout_par_provider, labels=cout_par_provider.index, autopct="%1.0f%%", startangle=90)
ax1.set_title("Répartition de la dépense mensuelle projetée par fournisseur cloud")
fig1.savefig("figure6_repartition_couts.png", dpi=200, bbox_inches="tight")

# Figure 7 : Évolution mensuelle des coûts
fig2, ax2 = plt.subplots(figsize=(9, 4))
ax2.plot(evolution_mensuelle.index, evolution_mensuelle.values, marker="o", markersize=3)
ax2.set_ylabel("Dépense mensuelle projetée (€)")
ax2.set_title("Évolution de la dépense cloud projetée (24 mois)")
plt.xticks(rotation=60, fontsize=7)
fig2.tight_layout()
fig2.savefig("figure7_evolution_couts.png", dpi=200, bbox_inches="tight")

# Figure 8 : Ressources zombies vs ressources normales
fig3, ax3 = plt.subplots(figsize=(7, 4))
categories = ["Ressources normales", "Ressources 'zombies'\n(coûteuses et sous-utilisées)"]
counts = [len(df) - len(zombies), len(zombies)]
colors = ["#2E7D6B", "#C0504D"]
ax3.bar(categories, counts, color=colors)
ax3.set_ylabel("Nombre de ressources")
ax3.set_title("Détection des ressources sous-utilisées (\"zombies\")")
fig3.savefig("figure8_taux_utilisation.png", dpi=200, bbox_inches="tight")

print("\nLes 3 figures ont été générées avec succès dans le dossier courant.")

# -------------------------------------------------------------
# 5. EXPORT POUR POWER BI
# -------------------------------------------------------------
# Ce fichier CSV peut être importé directement dans Power BI Desktop
# (Get Data -> Text/CSV) pour construire un tableau de bord interactif.
colonnes_export = ["Resource_ID", "Region", "Cloud_Provider", "Resource_Status",
                    "Resource_Type", "Creation_Date", "Hourly_Cost",
                    "CPU_Utilization_Pct", "Projected_Monthly_Spend"]
df["Is_Zombie"] = ((df["Hourly_Cost"] > seuil_cout) & (df["CPU_Utilization_Pct"] < seuil_cpu))
df[colonnes_export + ["Is_Zombie"]].to_csv("dataset_finops_powerbi.csv", index=False)
print("Fichier 'dataset_finops_powerbi.csv' exporté, prêt à être importé dans Power BI.")


import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

# -------------------------------------------------------------
# 4. INGESTION VERS SNOWFLAKE
# -------------------------------------------------------------
print("\n--- DEBUT INGESTION SNOWFLAKE ---")

# Remplacez VOTRE_MOT_DE_PASSE et VOTRE_COMPTE (ex: 12345ABCD)
conn = snowflake.connector.connect(
    user='ACCOUNTADMIN',
    password='VOTRE_MOT_DE_PASSE',
    account='VOTRE_COMPTE',
    warehouse='MON_WH',
    database='MON_PROJET_DB',
    schema='MON_PROJET_SCHEMA'
)

# Conversion des noms de colonnes en majuscules pour Snowflake
df.columns = [col.upper() for col in df.columns]

# Envoi du DataFrame nettoyé dans la table
success, nchunks, nrows, _ = write_pandas(
    conn=conn,
    df=df,
    table_name='DONNEES_ANALYSE',
    auto_create_table=False
)

print(f"Succès de l'ingestion : {success}")
print(f"Lignes insérées dans Snowflake : {nrows}")

conn.close()

import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

print("\n--- DEBUT INGESTION SNOWFLAKE ---")

# Remplacez VOTRE_MOT_DE_PASSE et VOTRE_COMPTE par vos identifiants réels
conn = snowflake.connector.connect(
    user='ACCOUNTADMIN',
    password='VOTRE_MOT_DE_PASSE',
    account='VOTRE_COMPTE',  # Exemple: '12345ABCD'
    warehouse='MON_WH',
    database='MON_PROJET_DB',
    schema='MON_PROJET_SCHEMA'
)

# Alignement des noms de colonnes en majuscules pour Snowflake
df.columns = [col.upper() for col in df.columns]

# Envoi du DataFrame dans Snowflake
success, nchunks, nrows, _ = write_pandas(
    conn=conn,
    df=df,
    table_name='DONNEES_ANALYSE',
    auto_create_table=False
)

print(f"Succès de l'ingestion : {success}")
print(f"Lignes insérées dans Snowflake : {nrows}")

conn.close()
df.columns = [col.upper() for col in df.columns]


import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

print("1. Connexion à Snowflake en cours...")
try:
    conn = snowflake.connector.connect(
        user='ACCOUNTADMIN',
        password='VOTRE_MOT_DE_PASSE',
        account='VOTRE_COMPTE',  # ex: xy12345.eu-west-1
        warehouse='MON_WH',
        database='MON_PROJET_DB',
        schema='MON_PROJET_SCHEMA'
    )
    print("-> SUCCÈS : Connexion établie avec succès !")
except Exception as e:
    print(f"-> ERREUR DE CONNEXION : {e}")
    exit()

# Création d'un petit DataFrame de test pour la garantie
df_test = pd.DataFrame({
    'CLOUD_PROVIDER': ['AWS', 'Azure', 'GCP'],
    'PROJECTED_MONTHLY_SPEND': [150.5, 300.0, 120.4],
    'IS_ZOMBIE': [True, False, True]
})

# Forcer les en-têtes en majuscules (obligatoire pour Snowflake)
df_test.columns = [col.upper() for col in df_test.columns]

print("2. Envoi des données vers Snowflake...")
success, nchunks, nrows, _ = write_pandas(
    conn=conn,
    df=df_test,
    table_name='TEST_GARANTIE',
    auto_create_table=True  # Crée la table automatiquement si elle n'existe pas
)

print(f"-> SUCCÈS DE L'ENVOI : {success}")
print(f"-> GARANTIE : {nrows} lignes insérées dans la table 'TEST_GARANTIE'.")

conn.close()