import os
import requests

# Récupération de l'URL du Webhook depuis l'environnement (ou URL de test)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://webhook.site/votre-url-unique")

# Données FinOps du projet
economie_totale = 158220.20
seuil_alerte = 50000.00
nb_zombies = 77

if economie_totale > seuil_alerte:
    payload = {
        "status": "ALERTE CRITIQUE FINOPS",
        "timestamp": "2026-10-16 08:00:00 UTC",
        "metrics": {
            "zombie_resources": f"{nb_zombies} sur 800 (14.4%)",
            "potential_monthly_savings": f"{economie_totale:,.2f} EUR",
            "threshold": f"{seuil_alerte:,.2f} EUR"
        },
        "top_priorities": [
            {"id": "RES-00275", "cloud": "AWS (Us-East-1)", "cost": "8 942,50 EUR/mois"},
            {"id": "RES-00504", "cloud": "Google Cloud (Us-West-2)", "cost": "3 985,80 EUR/mois"},
            {"id": "RES-00580", "cloud": "AWS (Eu-West-1)", "cost": "3 920,10 EUR/mois"},
            {"id": "RES-00651", "cloud": "AWS (Ap-South-1)", "cost": "3 664,60 EUR/mois"},
            {"id": "RES-00105", "cloud": "AWS (Eu-West-1)", "cost": "3 365,30 EUR/mois"}
        ],
        "message": "Seuil critique dépassé. Action de remédiation requise sur l'entrepôt Snowflake et le dashboard Streamlit."
    }

    response = requests.post(WEBHOOK_URL, json=payload)
    
    if response.status_code == 200:
        print("[SUCCESS] Webhook FinOps transmis avec succès.")
    else:
        print(f"[ERREUR] Échec de transmission : {response.status_code}")
else:
    print("[INFO] Seuil non atteint, aucune alerte déclenchée.")