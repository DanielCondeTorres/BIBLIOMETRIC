import pandas as pd
import matplotlib.pyplot as plt

# Leer el archivo CSV
df = pd.read_csv('Scopus_VR_ED_only_2024.csv')

# Seleccionar las columnas relevantes y limpiar datos
df = df[['Year', 'Cited by']].dropna()
df['Year'] = df['Year'].astype(int)

# Calcular promedio anual de citas por año de publicación
yearly_avg = df.groupby('Year')['Cited by'].mean().reset_index()

# Crear la gráfica
plt.figure(figsize=(10, 6))
plt.plot(yearly_avg['Year'], yearly_avg['Cited by'], marker='o')
plt.title('Average Total Citations per Publication Year')
plt.xlabel('Publication Year',fontsize=20)
plt.ylabel('Average Total Citations',fontsize=20)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.grid(True)
plt.tight_layout()
plt.show()
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                 
