"""Surveillance FinOps planifiée : détecte les ressources sous-utilisées et envoie une alerte e-mail.

Exécution :
    python monitoring_zombies.py [chemin_csv]

Variables d'environnement (facultatives ; sans SMTP_HOST, l'alerte est seulement journalisée) :
    SMTP_HOST, SMTP_PORT (587), SMTP_USER, SMTP_PASSWORD,
    SMTP_STARTTLS (1 par défaut), ALERT_FROM, ALERT_TO
"""

from __future__ import annotations

import os
import smtplib
import ssl
import sys
from datetime import datetime
from email.message import EmailMessage

import pandas as pd

SEUIL_COUT_HORAIRE = 1.5        # euros par heure
SEUIL_CPU_PCT = 15              # pourcentage d'utilisation CPU
SEUIL_ALERTE_ECONOMIE = 50000   # euros par mois : au-delà, l'alerte est critique
JOURNAL = "journal_alertes_finops.log"
CSV_PAR_DEFAUT = "dataset_finops_powerbi.csv"


def formater_euros(montant):
    """Format français : 158 220,20 €."""
    return f"{montant:,.2f} €".replace(",", " ").replace(".", ",").replace(" €", " €")


def charger_donnees(chemin_csv):
    """Charge le dernier export de données de consommation cloud."""
    df = pd.read_csv(chemin_csv)
    df["Creation_Date"] = pd.to_datetime(df["Creation_Date"])
    return df


def detecter_ressources_zombies(df, seuil_cout=SEUIL_COUT_HORAIRE, seuil_cpu=SEUIL_CPU_PCT):
    """Règle métier FinOps : coût horaire supérieur au seuil ET CPU inférieur au seuil."""
    return df[(df["Hourly_Cost"] > seuil_cout) & (df["CPU_Utilization_Pct"] < seuil_cpu)]


def construire_alerte(zombies, seuil_alerte=SEUIL_ALERTE_ECONOMIE):
    """Retourne le niveau, les indicateurs et le contenu de l'alerte (sujet et corps)."""
    horodatage = datetime.now().strftime("%Y-%m-%d %H:%M")
    nb = len(zombies)
    economie = float(zombies["Projected_Monthly_Spend"].sum()) if nb else 0.0
    niveau = "CRITIQUE" if economie > seuil_alerte else "INFO"

    corps = (
        f"Rapport de surveillance FinOps — {horodatage}\n"
        f"{'-' * 55}\n"
        f"Niveau : {niveau}\n"
        f"Ressources sous-utilisées détectées : {nb}\n"
        f"Économie mensuelle potentielle : {formater_euros(economie)}\n"
        f"Seuil d'alerte : {formater_euros(seuil_alerte)} par mois\n"
    )
    if nb:
        top5 = zombies.sort_values("Projected_Monthly_Spend", ascending=False).head(5)
        corps += "\nTop 5 ressources à traiter en priorité :\n"
        for _, r in top5.iterrows():
            corps += (f"  - {r['Resource_ID']} ({r['Cloud_Provider']}, {r['Resource_Type']}) : "
                      f"{formater_euros(r['Projected_Monthly_Spend'])} par mois\n")
    sujet = f"[{niveau}] Surveillance FinOps : {nb} ressources, {formater_euros(economie)} par mois"
    return {"niveau": niveau, "nb": nb, "economie": economie, "sujet": sujet, "corps": corps}


def envoyer_email(sujet, corps, env=None):
    """Envoie l'alerte par SMTP. Lève une erreur claire si la configuration est incomplète."""
    env = os.environ if env is None else env

    def valeur(nom):
        return (env.get(nom) or "").strip()

    manquants = [c for c in ("SMTP_HOST", "SMTP_PORT", "ALERT_TO") if not valeur(c)]
    if not valeur("ALERT_FROM") and not valeur("SMTP_USER"):
        manquants.append("ALERT_FROM ou SMTP_USER")
    if valeur("SMTP_USER") and not valeur("SMTP_PASSWORD"):
        manquants.append("SMTP_PASSWORD")
    if manquants:
        raise RuntimeError("Alerte critique non envoyée : variables absentes ou vides : " + ", ".join(manquants))

    try:
        port = int(valeur("SMTP_PORT"))
    except ValueError as erreur:
        raise RuntimeError(f"SMTP_PORT doit être un nombre, reçu : {valeur('SMTP_PORT')!r}") from erreur

    msg = EmailMessage()
    msg["Subject"] = sujet
    msg["From"] = valeur("ALERT_FROM") or valeur("SMTP_USER")
    msg["To"] = valeur("ALERT_TO")
    msg.set_content(corps)

    with smtplib.SMTP(valeur("SMTP_HOST"), port, timeout=20) as smtp:
        if (env.get("SMTP_STARTTLS") or "1").strip() == "1":
            smtp.starttls(context=ssl.create_default_context())
        if valeur("SMTP_USER"):
            smtp.login(valeur("SMTP_USER"), valeur("SMTP_PASSWORD"))
        smtp.send_message(msg)
    print("E-mail d'alerte envoyé.")
    return True


def journaliser(texte):
    """Trace l'alerte dans un journal local (archivé comme artefact par GitHub Actions)."""
    with open(JOURNAL, "a", encoding="utf-8") as f:
        f.write(texte + "\n" + "=" * 55 + "\n")


def ecrire_sortie_github(alerte):
    """Expose le résultat à la suite du workflow (étape conditionnelle)."""
    chemin = os.environ.get("GITHUB_OUTPUT")
    if chemin:
        with open(chemin, "a", encoding="utf-8") as f:
            f.write(f"alerte={'true' if alerte else 'false'}\n")


def executer_cycle_surveillance(chemin_csv=CSV_PAR_DEFAUT, env=None):
    """Point d'entrée : détection, journal, puis e-mail si l'alerte est critique."""
    df = charger_donnees(chemin_csv)
    zombies = detecter_ressources_zombies(df)
    alerte = construire_alerte(zombies)
    print(alerte["corps"])
    journaliser(alerte["corps"])
    envoye = False
    if alerte["niveau"] == "CRITIQUE":
        envoye = envoyer_email(alerte["sujet"], alerte["corps"], env=env)
    ecrire_sortie_github(alerte["niveau"] == "CRITIQUE")
    return {**alerte, "envoye": envoye}


if __name__ == "__main__":
    executer_cycle_surveillance(sys.argv[1] if len(sys.argv) > 1 else CSV_PAR_DEFAUT)
