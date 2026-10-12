import pandas as pd
from datetime import datetime

SEUIL_COUT_HORAIRE = 1.5
SEUIL_CPU_PCT = 15
SEUIL_ALERTE_ECONOMIE = 50000

def charger_donnees(chemin_csv):
    """Charge le CSV de manière sécurisée en évitant les erreurs de colonnes."""
    try:
        df = pd.read_csv(chemin_csv)
    except Exception:
        df = pd.read_csv(chemin_csv, header=None)

    noms_attendus = [
        "Resource_ID", "Region", "Cloud_Provider", "Status", 
        "Resource_Type", "Creation_Date", "Hourly_Cost", 
        "CPU_Utilization_Pct", "Projected_Monthly_Spend", "Is_Zombie"
    ]
    
    if len(df.columns) == len(noms_attendus):
        df.columns = noms_attendus
    elif "Creation_Date" not in df.columns:
        df.columns = noms_attendus[:len(df.columns)]

    if "Creation_Date" in df.columns:
        df["Creation_Date"] = pd.to_datetime(df["Creation_Date"], errors="coerce")
    
    df["Hourly_Cost"] = pd.to_numeric(df["Hourly_Cost"], errors="coerce")
    df["CPU_Utilization_Pct"] = pd.to_numeric(df["CPU_Utilization_Pct"], errors="coerce")
    
    if "Projected_Monthly_Spend" not in df.columns:
        df["Projected_Monthly_Spend"] = df["Hourly_Cost"] * 730
    else:
        df["Projected_Monthly_Spend"] = pd.to_numeric(df["Projected_Monthly_Spend"], errors="coerce")

    return df

def detecter_ressources_zombies(df, seuil_cout=SEUIL_COUT_HORAIRE, seuil_cpu=SEUIL_CPU_PCT):
    zombies = df[(df["Hourly_Cost"] > seuil_cout) & (df["CPU_Utilization_Pct"] < seuil_cpu)]
    return zombies

def generer_rapport_alerte(zombies):
    horodatage = datetime.now().strftime("%Y-%m-%d %H:%M")
    nb = len(zombies)
    economie = zombies["Projected_Monthly_Spend"].sum() if "Projected_Monthly_Spend" in zombies.columns else 0

    niveau = "CRITIQUE" if economie > SEUIL_ALERTE_ECONOMIE else "INFO"

    message = (
        f"[{niveau}] Rapport de surveillance FinOps — {horodatage}\n"
        f"{'-'*55}\n"
        f"Ressources zombies détectées : {nb}\n"
        f"Économie mensuelle potentielle : {economie:,.2f} €\n"
    )
    return message

def envoyer_alerte(message):
    print(message)
    with open("journal_alertes_finops.log", "a", encoding="utf-8") as f:
        f.write(message + "\n" + "=" * 55 + "\n")

def executer_cycle_surveillance(chemin_csv=r"C:\Users\chikh\Downloads\dataset_finops_powerbi (1).csv"):
    df = charger_donnees(chemin_csv)
    print("\nAperçu du jeu de données chargé :")
    print(df.head())
    print(f"\nDimensions : {df.shape}")
    
    zombies = detecter_ressources_zombies(df)
    message = generer_rapport_alerte(zombies)
    envoyer_alerte(message)

if __name__ == "__main__":
    executer_cycle_surveillance()