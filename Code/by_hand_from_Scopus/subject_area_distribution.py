import matplotlib.pyplot as plt

# Datos
labels = ['Physics & Astronomy', 'Computer Science', 'Engineering', 'Mathematics',
          'Material Science', 'Chemistry', 'Decision Sciences', 'Others']
sizes = [30.3, 24.5, 15.1, 12.7, 9.7, 1.9, 1.4, 4.4]
colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0','#ffb3e6','#c2f0c2','#f0e68c']
explode = (0.1, 0.05, 0, 0, 0, 0, 0, 0)  # Resalta las dos áreas principales

# Crear gráfico de pastel
plt.figure(figsize=(8, 8))
plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors,
        startangle=140, explode=explode, shadow=True)
plt.title('Document Distribution by Subject Area')
plt.axis('equal')  # Asegura que el gráfico sea circular
plt.tight_layout()
plt.show()
