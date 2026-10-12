import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Configuration de la figure
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.axis('off') # Masquer les axes pour un rendu propre

# Coordonnées des 3 phases du cycle (disposition triangulaire)
centers = [(0, 0.75), (0.7, -0.4), (-0.7, -0.4)]

# Textes des nœuds adaptés au contexte de l'infrastructure Cloud
labels = [
    "1. Informer\n(Visibilité multi-cloud\n& Allocation)",
    "2. Optimiser\n(Détection de zombies\n& Redimensionnement)",
    "3. Opérer\n(Automatisation\n& Amélioration continue)"
]

# Couleurs associées aux phases : Bleu, Orange, Vert
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

# Dessin des cercles représentant les phases
for i, (x, y) in enumerate(centers):
    circle = mpatches.Circle((x, y), 0.38, color=colors[i], alpha=0.9, zorder=2)
    ax.add_patch(circle)
    ax.text(x, y, labels[i], ha='center', va='center', color='white', 
            fontweight='bold', fontsize=11, zorder=3)

# Configuration des flèches courbes reliant les phases pour créer le cycle
style = "Simple, tail_width=3, head_width=15, head_length=20"
kw = dict(arrowstyle=style, color="#555555", alpha=0.7)

# Tracé des flèches avec une courbure adaptée (arc3)
fleche_1 = mpatches.FancyArrowPatch((0.25, 0.5), (0.7, -0.05), connectionstyle="arc3,rad=-0.3", **kw)
fleche_2 = mpatches.FancyArrowPatch((0.3, -0.65), (-0.3, -0.65), connectionstyle="arc3,rad=-0.4", **kw)
fleche_3 = mpatches.FancyArrowPatch((-0.7, -0.05), (-0.25, 0.5), connectionstyle="arc3,rad=-0.3", **kw)

ax.add_patch(fleche_1)
ax.add_patch(fleche_2)
ax.add_patch(fleche_3)

# Ajout du titre
plt.title("Le Cycle de Vie FinOps", fontsize=16, fontweight='bold', y=0.95, color="#333333")
plt.tight_layout()

# Sauvegarde de l'image avec fond transparent
plt.savefig("schema_cycle_finops.png", dpi=300, bbox_inches='tight', transparent=True)
print("Image 'schema_cycle_finops.png' générée avec succès !")

# Affichage à l'écran
plt.show()