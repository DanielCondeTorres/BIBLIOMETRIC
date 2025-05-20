import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
# 1) Update this path to point to your CSV file
csv_path = 'datos_combinados.csv'

# 2) Read the CSV into a DataFrame
df = pd.read_csv(csv_path)

# 3) Create a helper column: list_of_authors = ["Name1", "Name2", ...]
#    - We split on ';'
#    - Then strip whitespace around each name
df['List_of_Authors'] = (
    df['Author full names']
      .fillna('')
      .apply(lambda cell: [name.strip() for name in cell.split(';') if name.strip()])
)

# 4) Compute number of authors for each row
df['Num_Authors'] = df['List_of_Authors'].apply(len)

# 5) Identify single‐authored papers
df['Is_Single_Authored'] = df['Num_Authors'] == 1

# 6) Count how many papers are single‐authored vs. multi‐authored
num_papers = len(df)
num_single = df['Is_Single_Authored'].sum()
num_multi = num_papers - num_single

print(f"Total papers:           {num_papers}")
print(f"Single‐authored papers: {num_single}")
print(f"Multi‐authored papers:  {num_multi}\n")

# 7) Compute Collaboration Index (CI) = average number of authors per paper
CI = df['Num_Authors'].mean()
print(f"Collaboration Index (CI) = {CI:.3f}\n")

# 8) Compute Collaboration Coefficient (CC) as per Ajiferuke et al. (1988)
#    - We need f_j for j ≥ 1
#    - Only count papers with at least one author (Num_Authors ≥ 1)
freq = df['Num_Authors'].value_counts().sort_index()  # a Series: index = j, value = f_j
#    - Note: If there are any empty or NaN, they produce Num_Authors=0; we skip j=0 for CC.
N = num_papers
sum_fj_over_j = 0.0
for j, fj in freq.items():
    if j > 0:
        sum_fj_over_j += fj / j

CC = 1 - (sum_fj_over_j / N)
print(f"Collaboration Coefficient (CC) = {CC:.3f}\n")

# 9) (Optional) If you want to see the distribution f_j:
print("Number of papers by j authors (f_j):")
for j, fj in freq.items():
    if j > 0:
        print(f"  j = {j:2d} → {fj:4d} papers")

# 2) Read the CSV into a DataFrame
df = pd.read_csv(csv_path)

# 3) Divide "Author full names" en listas y cuenta autores
df['List_of_Authors'] = (
    df['Author full names']
      .fillna('')
      .apply(lambda cell: [name.strip() for name in cell.split(';') if name.strip()])
)
df['Num_Authors'] = df['List_of_Authors'].apply(len)

# 4) Calcula cuántos artículos hay para cada número de autores
author_counts = df['Num_Authors'].value_counts().sort_index()

# 5) Genera el histograma (gráfico de barras)
plt.figure(figsize=(10, 6))
plt.bar(author_counts.index, author_counts.values)

# --- Ajustes solicitados: xticks de 10 en 10, mayores tamaños de fuente --- #
max_authors = author_counts.index.max()
xtick_positions = np.arange(0, max_authors + 1, 10)  # 0, 10, 20, 30, …

plt.xticks(xtick_positions, fontsize=12)     # etiquetas del eje X con tamaño de fuente 12
plt.yticks(fontsize=12)                      # etiquetas del eje Y con tamaño de fuente 12

# Ajustar también el tamaño de los labels de ejes y título
plt.xlabel('Number of Authors', fontsize=14)
plt.ylabel('Number of Papers', fontsize=14)
plt.title('Distribution of Papers by Number of Authors', fontsize=16)

# Opcional: reforzar el tamaño de los ticks en ambos ejes
plt.tick_params(axis='both', which='major', labelsize=12)

plt.grid(axis='y', linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.show()


# Read the CSV (if you haven’t done so yet)
df = pd.read_csv(csv_path)

# 2) (Re)compute List_of_Authors and Num_Authors, if not already present
df['List_of_Authors'] = (
    df['Author full names']
      .fillna('')
      .apply(lambda cell: [name.strip() for name in cell.split(';') if name.strip()])
)
df['Num_Authors'] = df['List_of_Authors'].apply(len)

# 3) Find the maximum number of authors
max_authors = df['Num_Authors'].max()

# 4) Filter to the row(s) that have Num_Authors == max_authors
most_authored_papers = df[df['Num_Authors'] == max_authors]

# 5) Print out details (e.g., Title, Num_Authors, and Author full names)
print(f"Maximum number of authors on a single paper: {max_authors}\n")
print("Paper(s) with that author count:\n")
for idx, row in most_authored_papers.iterrows():
    title = row.get('Title', '<No Title Column>')
    authors_list = row['List_of_Authors']
    print(f"Index {idx}:")
    print(f"  Title       : {title}")
    print(f"  Num_Authors : {row['Num_Authors']}")
    print(f"  Full Names  : {row['Author full names']}")
    print("-" * 60)


# 2) Carga el CSV en un DataFrame
df = pd.read_csv(csv_path)

# 3) Divide "Author full names" en listas y cuenta autores
df['List_of_Authors'] = (
    df['Author full names']
      .fillna('')
      .apply(lambda cell: [name.strip() for name in cell.split(';') if name.strip()])
)
df['Num_Authors'] = df['List_of_Authors'].apply(len)

# 4) Calcula cuántos artículos hay para cada número de autores
author_counts = df['Num_Authors'].value_counts().sort_index()

# 5) Calcula el número total de autores distintos en todo el DataFrame
unique_authors = set()
for author_list in df['List_of_Authors']:
    for author in author_list:
        unique_authors.add(author)
total_distinct_authors = len(unique_authors)

# 6) Imprime el total de autores distintos
print(f"Total distinct authors: {total_distinct_authors}\n")

# 7) Genera el histograma (gráfico de barras)
plt.figure(figsize=(10, 6))
plt.bar(author_counts.index, author_counts.values)

# --- Ajustes solicitados: xticks de 10 en 10, mayores tamaños de fuente --- #
max_authors = author_counts.index.max()
xtick_positions = np.arange(0, max_authors + 1, 10)  # 0, 10, 20, 30, …

plt.xticks(xtick_positions, fontsize=12)     # etiquetas del eje X con tamaño de fuente 12
plt.yticks(fontsize=12)                      # etiquetas del eje Y con tamaño de fuente 12

# Ajustar también el tamaño de los labels de ejes y título
plt.xlabel('Number of Authors', fontsize=14)
plt.ylabel('Number of Papers', fontsize=14)
plt.title('Distribution of Papers by Number of Authors', fontsize=16)

# Opcional: reforzar el tamaño de los ticks en ambos ejes
plt.tick_params(axis='both', which='major', labelsize=12)

plt.grid(axis='y', linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.show()

