# ☁️ Optimization FinOps Multi-Cloud & Industrialisation CI/CD

[![CI Pipeline](https://github.com/chikhiabdessamad888-source/finops-cloud-optimisation/actions/workflows/ci.yml/badge.svg)](https://github.com/chikhiabdessamad888-source/finops-cloud-optimisation/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/chikhiabdessamad888-source/finops-cloud-optimisation)](https://github.com/chikhiabdessamad888-source/finops-cloud-optimisation/releases)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

## 📌 Contexte & Problématique
Réalisé dans le cadre du stage de première année d'ingénieur à l'ENSIAS au sein de **NTT DATA**, ce projet s'inscrit dans la démarche **FinOps** pour répondre aux dérives budgétaires liées au passage du modèle CapEx à l'OpEx dans le Cloud Computing. 

L'objectif est d'étudier si une règle combinant le coût horaire et le taux d'utilisation CPU permet d'identifier efficacement les ressources cloud coûteuses et sous-utilisées (*ressources zombies*), tout en évaluant la sensibilité de ces résultats aux hypothèses retenues et en garantissant la reproductibilité de la méthode.

## 🛠️ Démarche Méthodologique & Pipeline Analytique
1. **Génération & Nettoyage des Données :** En raison de la confidentialité des données de facturation (NDA), le projet s'appuie sur un jeu synthétique de **800 ressources sur 24 mois**, intégrant des anomalies contrôlées (coûts négatifs, taux > 100%, valeurs manquantes) corrigées lors du prétraitement (Pandas).
2. **Entreposage & Stockage (Data Warehouse) :** Ingestion et centralisation des données normalisées dans **Snowflake** (`FINOPSPROJET` dans `MON_PROJET_DB.PUBLIC`), permettant d'exécuter des requêtes SQL de vérification et de reproductibilité.
3. **Algorithme de Détection :** Application d'une règle métier combinant un seuil de coût horaire ($> 1,50\,€/h$) et un taux d'utilisation processeur ($< 15\,\%$).
4. **Restitution Interactive :** Tableau de bord **Streamlit** (`app.py`) permettant l'ajustement dynamique des seuils et l'exploration par fournisseur (AWS, Azure, Google Cloud), région et type de ressource.
5. **Gouvernance & Industrialisation (CI/CD/CT) :** Automatisation via **GitHub Actions** comprenant l'intégration continue (`ci.yml`), le déploiement continu (`cd.yml` pour les releases comme `v1.0.0`) et la surveillance planifiée (`monitoring.yml`).

## 📁 Structure du Projet
```text
finops-cloud-optimisation/
├── .github/
│   └── workflows/          # Workflows CI (ci.yml), CD (cd.yml) et surveillance (monitoring.yml)
├── tests/                  # Suite de tests unitaires automatisés (pytest)
│   └── test_finops.py
├── analyse_consommation_cloud.py  # Module de génération, nettoyage et prétraitement ETL
├── monitoring_zombies.py          # Script de détection automatisée des ressources zombies
├── app.py                         # Tableau de bord interactif Streamlit
├── pyproject.toml                 # Configuration des linter (Ruff) et tests (Pytest)
└── requirements.txt               # Dépendances figées du projet (pandas, snowflake-connector-python, streamlit, etc.)
