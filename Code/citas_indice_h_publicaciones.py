import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np


def custom_viridis_with_black(n):
    viridis = cm.get_cmap('viridis', n - 1)  # n-1 colores de viridis
    colors = viridis(np.linspace(0, 1, n - 1))
    black = np.array([[0, 0, 0, 1]])  # RGBA para negro
    colors = np.vstack([black, colors])  # poner negro al inicio
    return mcolors.ListedColormap(colors)


# --- FUNCIÓN PARA GRAFICAR ---
def plot_horizontal_bar(labels, values, title, xlabel, filename=None, adjust_xlim=False, text_sep=0.1):
    
    colors = cm.viridis(np.linspace(0, 0.6, len(labels)))

    plt.figure(figsize=(12, 6))
    bars = plt.barh(labels[::-1],
                    values[::-1],
                    color=colors[::-1],
                    edgecolor='black',
                    linewidth=0.5)
    plt.xlabel(xlabel, weight='bold', size=15)
    plt.xticks(size=15)
    plt.yticks(size=12)
    plt.title(title, weight='bold', size=20)

    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    for bar in bars:
        width = bar.get_width()
        plt.text(width + float(text_sep), bar.get_y() + bar.get_height() / 2,
                 f'{int(width)}', va='center', ha='left', weight='bold', size=15)
        
#Ajusta el valor que esta en la barra horizontal solo si se incluye como argumento
    if adjust_xlim:
        plt.xlim(right=max(values) + max(text_sep * 3, 5))

    plt.tight_layout(pad=1, w_pad=2, h_pad=2)

    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
    else:
        plt.show()

# --- CARGA Y PROCESAMIENTO DE DATOS ---
file_path = 'Scopus_VR_ED_only_2024.csv'
df = pd.read_csv(file_path, low_memory=False)
df.columns = df.columns.str.strip()

# Extraer y limpiar nombres de autores
all_authors = df['Author full names'].dropna().str.split('; ').sum()
author_names = [a.split(' (')[0].strip() for a in all_authors]
author_counts = Counter(author_names)
top_authors_by_publications = author_counts.most_common(10)

# Crear diccionario de afiliaciones
autor_afiliaciones = {}
for _, row in df.iterrows():
    if pd.isna(row['Author full names']) or pd.isna(row['Affiliations']):
        continue
    authors = [a.split(' (')[0].strip() for a in row['Author full names'].split('; ')]
    affiliations = [a.strip() for a in str(row['Affiliations']).split(';')]
    for i, author in enumerate(authors):
        if author not in autor_afiliaciones:
            if i < len(affiliations):
                base_affil = affiliations[i].split(',')[0].strip()
                autor_afiliaciones[author] = base_affil
else:
    autor_afiliaciones[author] = "Affiliation not found"

# --- GRÁFICO 1: Publicaciones ---
authors_pub, counts_pub = zip(*top_authors_by_publications)
labels_pub = [f"{a}\n({autor_afiliaciones.get(a, 'No affiliation')})" for a in authors_pub]
plot_horizontal_bar(labels_pub, counts_pub, 'Top 10 most prolific authors', 'Number of documents',
                    'top_authors_by_publications.png', adjust_xlim=False, text_sep=0.1)

# --- Cálculo índice h ---
def calcular_h_index(citaciones):
    citaciones_ordenadas = sorted(citaciones, reverse=True)
    return sum(c >= i + 1 for i, c in enumerate(citaciones_ordenadas))

# Citas por autor (solo para top por publicaciones)
autor_citas = {autor: [] for autor in dict(top_authors_by_publications)}
for _, row in df.iterrows():
    if pd.isna(row['Author full names']) or pd.isna(row['Cited by']):
        continue
    autores = [a.split(' (')[0].strip() for a in row['Author full names'].split('; ')]
    for autor in autores:
        if autor in autor_citas:
            autor_citas[autor].append(int(row['Cited by']))

# Índices h
h_indices = [(autor, calcular_h_index(citas)) for autor, citas in autor_citas.items()]
h_indices.sort(key=lambda x: x[1], reverse=True)
authors_h, h_values = zip(*h_indices)
labels_h = [f"{a}\n({autor_afiliaciones.get(a, 'No affiliation')})" for a in authors_h]
plot_horizontal_bar(labels_h, h_values, 'Top 10 Authors by H-Index', 'H-Index',
                    'top_authors_by_h_index.png', adjust_xlim=False, text_sep=0.1)

# --- GRÁFICO 3: Total de citas por autor (sin límite por publicaciones) ---
total_citas_autores = {}
for _, row in df.iterrows():
    if pd.isna(row['Author full names']) or pd.isna(row['Cited by']):
        continue
    autores = [a.split(' (')[0].strip() for a in row['Author full names'].split('; ')]
    for autor in autores:
        total_citas_autores[autor] = total_citas_autores.get(autor, 0) + int(row['Cited by'])

top_citados = sorted(total_citas_autores.items(), key=lambda x: x[1], reverse=True)[:10]
authors_cited, total_cited_values = zip(*top_citados)
labels_cited = [f"{a}\n({autor_afiliaciones.get(a, 'No affiliation')})" for a in authors_cited]
plot_horizontal_bar(labels_cited, total_cited_values, 'Top 10 Authors by Total Citations', 'Total Citations',
                    'top_total_citations.png', adjust_xlim=True, text_sep=10)
