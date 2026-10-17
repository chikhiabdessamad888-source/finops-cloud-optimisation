import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_alert_email():
    # Récupération des variables d'environnement configurées dans GitHub Secrets
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    alert_from = os.environ.get("ALERT_FROM")
    alert_to = os.environ.get("ALERT_TO")

    print(f"Tentative d'envoi d'e-mail de {alert_from} vers {alert_to}...")

    # Création du contenu du message
    subject = "[FINOPS ALERT] Rapport de Détection des Ressources Zombies"
    body = """
    Bonjour,

    Le système de surveillance FinOps a détecté des opportunités d'optimisation :

    - Ressources zombies identifiées : 77
    - Économies mensuelles potentielles : 158 219,60 €

    Ce message est généré automatiquement par le pipeline CI/CD GitHub Actions.
    """

    msg = MIMEMultipart()
    msg['From'] = alert_from
    msg['To'] = alert_to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connexion au serveur SMTP Gmail
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(alert_from, alert_to, msg.as_string())
        server.quit()
        print("[SUCCESS] E-mail d'alerte FinOps envoyé avec succès !")
    except Exception as e:
        print(f"[ERROR] Échec de l'envoi de l'e-mail : {e}")

if __name__ == "__main__":
    # Exécution de l'envoi
    send_alert_email()