import matplotlib.pyplot as plt

# Datos del Panel A (Tipo de documento)
labels_A = ['Article', 'Conference Paper', 'Review', 'Book Chapter', 'Book']
sizes_A = [63.2, 31.6, 2.5, 2.0, 0.7]
colors_A = ['#66b3ff', '#99ff99', '#ffcc99', '#ff9999', '#c2c2f0']

# Datos del Panel B (Área temática)
labels_B = ['Physics & Astronomy', 'Computer Science', 'Engineering', 'Mathematics',
            'Material Science', 'Chemistry', 'Others']
sizes_B = [30.3, 24.5, 15.1, 12.7, 9.7, 1.9, 5.8]
print(sum(sizes_B))
colors_B = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0','#ffb3e6','#c2f0c2','#f0e68c']

# Crear la figura y dos subgráficos
fig, axs = plt.subplots(1, 2, figsize=(14, 7))

# Panel A: Tipo de documento
wedges_A, texts_A, autotexts_A = axs[0].pie(
    sizes_A,
    labels=labels_A,
    autopct='%1.1f%%',
    startangle=140,
    colors=colors_A,
    wedgeprops=dict(width=0.4),
    textprops=dict(color="black", fontsize=12)
)
centre_circle_A = plt.Circle((0, 0), 0.70, fc='white')
axs[0].add_artist(centre_circle_A)
axs[0].set_title('A. Document Types', fontsize=14,weight='bold')

# Panel B: Área temática
wedges_B, texts_B, autotexts_B = axs[1].pie(
    sizes_B,
    labels=labels_B,
    autopct='%1.1f%%',
    startangle=140,
    colors=colors_B,
    #wedgeprops=dict(width=0.4),
    textprops=dict(color="black", fontsize=14)
)
#centre_circle_B = plt.Circle((0, 0), 0.70, fc='white')
#axs[1].add_artist(centre_circle_B)
axs[1].set_title('B. Subject Areas', fontsize=14, weight='bold')

# Estilo de texto para los porcentajes
for autotext in autotexts_A + autotexts_B:
    autotext.set_color('black')
    autotext.set_fontsize(8)
    #autotext.set_weight('bold')

plt.tight_layout()
plt.show()
