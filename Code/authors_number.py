
import pandas as pd

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
