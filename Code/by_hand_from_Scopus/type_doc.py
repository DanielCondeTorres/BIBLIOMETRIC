import matplotlib.pyplot as plt

# Datos
labels = ['Article', 'Conference Paper', 'Review', 'Book Chapter',
          'Book']
sizes = [63.2, 31.6, 2.5, 2.0, 0.7]#, 1.9, 1.4, 4.4]
colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0','#ffb3e6','#c2f0c2','#f0e68c']

explode = (0.1, 0.05, 0, 0, 0)#, 0, 0, 0)
# Crear gráfico tipo donut
plt.figure(figsize=(9, 9))
wedges, texts, autotexts = plt.pie(
    sizes,
    labels=labels,
    autopct='%1.1f%%',
    startangle=140,
    colors=colors,
    explode=explode,
    wedgeprops=dict(width=0.4),  # Anillo sin sombra
    textprops=dict(color="black", fontsize=14)  # Estilo para etiquetas
)

# Ajustar estilos de porcentajes
for autotext in autotexts:
    autotext.set_color('black')
    autotext.set_fontsize(13)
    #autotext.set_weight('bold')

# Añadir círculo blanco al centro
centre_circle = plt.Circle((0, 0), 0.70, fc='white')
fig = plt.gcf()
fig.gca().add_artist(centre_circle)

# Título y presentación
plt.title('Document Distribution by Subject Area (Donut Chart)', fontsize=14, weight='bold')
plt.axis('equal')
plt.tight_layout()
plt.show()
