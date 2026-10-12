import streamlit as st
import pandas as pd

st.set_page_config(page_title="FinOps Ops Portal", layout="wide")

st.title("⚡ Portail Opérationnel FinOps — Détection Zombie & Simulation")
st.markdown("Outil interactif pour ajuster les seuils de détection et exporter les listes de remédiation.")

# 1. Sidebar - Configuration
st.sidebar.header("⚙️ Configuration des Seuils")
cpu_threshold = st.sidebar.slider("Seuil CPU Maximum (%)", min_value=1, max_value=50, value=15)
cost_threshold = st.sidebar.slider("Seuil Coût Horaire Minimum (€)", min_value=0.1, max_value=10.0, value=1.5, step=0.1)

# 2. Génération de données
@st.cache_data
def load_data():
    return pd.DataFrame({
        "ResourceId": [f"RES-{i:03d}" for i in range(1, 801)],
        "ProviderName": ["AWS", "Azure", "GCP"] * 266 + ["AWS"] * 2,
        "ResourceType": ["VirtualMachine", "Database", "StorageVolume"] * 266 + ["VirtualMachine"] * 2,
        "Region": ["eu-west-1", "eu-west-3", "us-east-1"] * 266 + ["eu-west-1"] * 2,
        "CpuUtilizationPct": pd.Series([8, 12, 45, 3, 80, 14, 5, 95] * 100),
        "HourlyCost": pd.Series([1.8, 2.1, 0.5, 3.0, 4.2, 1.6, 0.8, 5.0] * 100),
    })

df = load_data()

# 3. Filtrage des ressources zombies
zombies = df[(df["CpuUtilizationPct"] < cpu_threshold) & (df["HourlyCost"] > cost_threshold)]
total_monthly_savings = zombies["HourlyCost"].sum() * 730

# 4. KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ressources Analysées", len(df))
col2.metric("Ressources Zombies", len(zombies), delta=f"{len(zombies)/len(df)*100:.1f}%", delta_color="inverse")
col3.metric("Gaspillage Mensuel", f"{total_monthly_savings:,.2f} €")
col4.metric("Réduction Estimée", f"{(total_monthly_savings / (df['HourlyCost'].sum() * 730)) * 100:.1f}%")

st.divider()

# 5. Affichage du tableau & Export
st.subheader("📋 Liste des Ressources à Réformer")
st.dataframe(zombies, use_container_width=True)

csv_data = zombies.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Télécharger la liste d'action (CSV)",
    data=csv_data,
    file_name="finops_zombie_resources.csv",
    mime="text/csv"
)
