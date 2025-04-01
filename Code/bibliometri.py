import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import matplotlib as mpl
import os
import re
from collections import Counter
import pycountry
from matplotlib.colors import ListedColormap


import math
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.cm import hsv

def generate_colormap(N):
    arr = np.arange(N)/N
    N_up = int(math.ceil(N/7)*7)
    arr.resize(N_up)
    arr = arr.reshape(7,N_up//7).T.reshape(-1)
    ret = mpl.cm.hsv(arr)
    n = ret[:,3].size
    a = n//2
    b = n-a
    for i in range(3):
        ret[0:n//2,i] *= np.arange(0.2,1,0.8/a)
    ret[n//2:,3] *= np.arange(1,0.1,-0.9/b)
#     print(ret)
    return ret
mpl.use('Agg')
# Style configuration
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 7)
plt.rcParams['font.size'] = 12

def plot_yearly_publications(scopus_file):
    try:
        # Read file with automatic encoding detection
        encodings = ['utf-8', 'ISO-8859-1', 'latin1']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(scopus_file, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        # Find year column (Scopus may use different names)
        year_cols = ['Year', 'Publication Year', 'Year of Publication']
        year_col = next((col for col in year_cols if col in df.columns), None)
        
        if year_col is None:
            raise ValueError("No column with year information found")
        
        # Clean year data and filter up to 2024
        df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
        df = df.dropna(subset=[year_col])
        df[year_col] = df[year_col].astype(int)
        df = df[df[year_col] <= 2024]  # Filter for years up to 2024
        
        # Count publications per year and sort
        counts = df[year_col].value_counts().sort_index()
        
        # Fill missing years for continuous plot
        if not counts.empty:
            all_years = range(min(counts.index), max(counts.index)+1)
            complete_counts = defaultdict(int, counts)
            for year in all_years:
                complete_counts[year]  # Ensures all years exist
            
            # Convert to ordered Series
            complete_counts = pd.Series(complete_counts).sort_index()
            
            # Create figure
            fig, ax = plt.subplots(figsize=(14, 7))
            
            # Bar plot with color gradient
            bars = ax.bar(complete_counts.index, complete_counts.values, 
                         color=sns.color_palette("Blues_d", len(complete_counts)))
            
            # Add trend line
            ax.plot(complete_counts.index, complete_counts.values, 
                   color='#e74c3c', marker='o', linestyle='--', linewidth=2, markersize=8)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(height)}',
                            ha='center', va='bottom', fontsize=14)
            
            # Customize plot
            ax.set_title('Annual Scientific Publications (Up to 2024)', pad=20, fontsize=16)
            ax.set_xlabel('Year', labelpad=10)
            ax.set_ylabel('Number of Publications', labelpad=10)
            ax.set_xticks(complete_counts.index)
            ax.set_xticklabels(complete_counts.index, rotation=45)
            
            # Add grid and final adjustments
            ax.grid(axis='y', alpha=0.3)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            plt.tight_layout()
            plt.show()
            plt.savefig('publicaciones_anuales.jpg', dpi=300, bbox_inches='tight')

            return complete_counts
            
        else:
            print("No data available for years up to 2024")
            return None
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def get_country(affiliation_text):
    """Extract country from affiliation string"""
    if not isinstance(affiliation_text, str):
        return 'Unknown'
    
    # Common patterns for country extraction
    patterns = [
        r',\s*([A-Za-z\s]+?)\s*(?:,\s*\d{5}|$)',
        r',\s*([A-Za-z\s]+?)\s*$',
        r'\[([A-Za-z\s]+)\]'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, affiliation_text)
        if match:
            country_candidate = match.group(1).strip()
            try:
                # Try to match with pycountry database
                country = pycountry.countries.search_fuzzy(country_candidate)[0].name
                return country
            except:
                # If not found, return cleaned candidate
                return country_candidate
    
    return 'Unknown'

def analyze_scopus_authors(scopus_file, output_folder='scopus_analysis', top_n=10):
    try:
        # Setup output directory
        os.makedirs(output_folder, exist_ok=True)
        
        # Read file with encoding detection
        encodings = ['utf-8', 'ISO-8859-1', 'latin1', 'windows-1252']
        df = None
        for enc in encodings:
            try:
                df = pd.read_csv(scopus_file, encoding=enc, low_memory=False)
                break
            except (UnicodeDecodeError, pd.errors.EmptyDataError) as e:
                continue
        
        if df is None:
            raise ValueError("Failed to read the file with tested encodings")
        
        # Check required columns
        if 'Authors with affiliations' not in df.columns:
            raise ValueError("Required column 'Authors with affiliations' missing")
        
        # Process author data
        author_data = []
        
        for affil_text in df['Authors with affiliations'].dropna():
            authors = re.split(r';\s*(?=[A-ZÀ-ÿ])', str(affil_text))
            for author in authors:
                if ',' in author:
                    try:
                        # Extract author name
                        name = re.sub(r'\([^)]*\)', '', author.split(',')[0]).strip()
                        name = re.sub(r'^\d+\s*', '', name).strip()
                        
                        # Extract affiliation info
                        affil_parts = author.split(',')[1:]
                        institution = affil_parts[0].strip() if affil_parts else 'Unknown'
                        institution = re.sub(r'\[.*?\]', '', institution).split('(')[0].strip()
                        
                        # Extract country
                        country = get_country(author)
                        
                        if name and institution:
                            author_data.append({
                                'author': name,
                                'institution': institution,
                                'country': country
                            })
                    except Exception as e:
                        continue
        
        # Create DataFrame
        authors_df = pd.DataFrame(author_data)
        
        if authors_df.empty:
            raise ValueError("No valid author data found")
        
        # Count publications per author
        author_counts = authors_df['author'].value_counts().head(top_n)
        
        # Get main institution and country for each top author
        top_authors = []
        for author, count in author_counts.items():
            author_records = authors_df[authors_df['author'] == author]
            
            # Get most common institution
            if not author_records.empty:
                main_institution = author_records['institution'].mode()[0]
                country = author_records['country'].mode()[0]
            else:
                main_institution = 'Unknown'
                country = 'Unknown'
            
            top_authors.append({
                'Author': author,
                'Publications': count,
                'Institution': main_institution,
                'Country': country,
                'Contribution %': round((count / len(df)) * 100, 2)
            })
        
        top_authors_df = pd.DataFrame(top_authors)
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(20, 14))
        
        # Create labels with institution and country
        labels = [
            f"{row['Author']}\n{row['Institution']}\n({row['Country']})"
            for _, row in top_authors_df.iterrows()
        ]
        
        # Horizontal bar plot
        bars = ax.barh(
            labels,
            top_authors_df['Publications'],
            color=sns.color_palette("mako_r", len(top_authors_df))
        )
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width - 0.3,
                bar.get_y() + bar.get_height()/2,
                f'{int(width)}',
                ha='right',
                va='center',
                color='white',
                fontweight='bold',
                fontsize=12
            )
        
        # Customize plot
        ax.set_title(
            f'Top {top_n} Most Productive Authors with Affiliations\n(Total Publications: {len(df):,})',
            pad=25,
            fontsize=18
        )
        ax.set_xlabel('Number of Publications', labelpad=15, fontsize=14)
        ax.set_ylabel('Author (Institution, Country)', labelpad=15, fontsize=14)
        ax.grid(axis='x', alpha=0.2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Save results
        output_img = os.path.join(output_folder, 'top_authors_affiliations_countries.png')
        plt.savefig(output_img, dpi=300, bbox_inches='tight', facecolor='white')
        
        output_csv = os.path.join(output_folder, 'top_authors_details.csv')
        top_authors_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        
        print(f"\nAnalysis results saved:")
        print(f"- Visualization: {output_img}")
        print(f"- Complete data: {output_csv}")
        
        plt.tight_layout()
        plt.show()
        
        return top_authors_df
        
    except Exception as e:
        print(f"Processing error: {str(e)}")
        return None




def analyze_countries(scopus_file, output_folder='country_analysis'):
    """Analyze production and citations by country"""
    try:
        # Create output directory
        os.makedirs(output_folder, exist_ok=True)
        
        # Read file with encoding detection
        encodings = ['utf-8', 'ISO-8859-1', 'latin1', 'windows-1252']
        df = None
        for enc in encodings:
            try:
                df = pd.read_csv(scopus_file, encoding=enc, low_memory=False)
                break
            except (UnicodeDecodeError, pd.errors.EmptyDataError) as e:
                continue
        
        if df is None:
            raise ValueError("Could not read file with tested encodings")
        
        # Verify required columns
        required_cols = ['Authors with affiliations', 'Cited by']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Required columns missing: {required_cols}")

        # Process country data
        production_data = defaultdict(int)
        citation_data = defaultdict(float)
        
        for _, row in df.iterrows():
            affil_text = str(row['Authors with affiliations'])
            citations = float(row['Cited by']) if pd.notna(row['Cited by']) else 0
            
            # Extract unique countries for this paper
            countries = set()
            authors = re.split(r';\s*(?=[A-ZÀ-ÿ])', affil_text)
            for author in authors:
                if ',' in author:
                    country = get_country(author)
                    if country != 'Unknown':
                        countries.add(country)
            
            # Distribute production and citations
            for country in countries:
                production_data[country] += 1
                citation_data[country] += citations / len(countries) if countries else 0
        
        # Convert to DataFrames
        production_df = pd.DataFrame(production_data.items(), columns=['Country', 'Publications'])
        citation_df = pd.DataFrame(citation_data.items(), columns=['Country', 'Citations'])
        
        # Sort and clean
        production_df = production_df.sort_values('Publications', ascending=False)
        citation_df = citation_df.sort_values('Citations', ascending=False)
        
        return production_df, citation_df
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        return None, None

def plot_country_data(country_df, metric, output_folder, top_n=15):
    """Generate country bar chart"""
    try:
        # Prepare data
        top_countries = country_df.head(top_n).sort_values(metric, ascending=True)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Horizontal bar plot
        bars = ax.barh(
            top_countries['Country'],
            top_countries[metric],
            color=sns.color_palette("viridis", len(top_countries))
        )
        
        # Add value labels

        for bar in bars:
            width = bar.get_width()
            ax.text(
                width - 0.3,
                bar.get_y() + bar.get_height()/2,
                f'{int(width) if metric == "Publications" else f"{int(width)}"}',
                ha='right',
                va='center',
                color='white',
                fontweight='bold',
                fontsize=12
            )
        # Customize plot
        title_metric = "Publications" if metric == "Publications" else "Citations"
        ax.set_title(f'Top {top_n} Countries by {title_metric}', pad=20, fontsize=16)
        ax.set_xlabel(title_metric, labelpad=10)
        ax.grid(axis='x', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Save results
        output_path = os.path.join(output_folder, f'top_countries_by_{metric.lower()}.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"Chart saved: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error generating chart: {str(e)}")
        return None

def analyze_bibliometric_metrics(scopus_file, output_folder='bibliometric_analysis'):
    """
    Analiza métricas de publicación y de citación a partir de un archivo Scopus.
    
    Métricas publicacionales:
      - Total Publications (TP)
      - Number of Contributing Authors (NCA)
      - Sole-authored Publications (SA)
      - Co-authored Publications (CA)
      - Collaboration Index (CI): Promedio de autores en publicaciones multi-autoria
      - Collaboration Coefficient (CC): 1 - (SA / TP)
    
    Métricas de citación:
      - Total Citations (TC)
      - Number of Cited Publications (NCP)
      - Proportion of Cited Publications (PCP)
      - Citations per Cited Publication (CCP)
      - h-index, g-index
      - i-index (i10, i100, i200)
    
    Science mapping:
      - Se indican como placeholders, ya que requieren análisis y datos adicionales.
    """
    os.makedirs(output_folder, exist_ok=True)
    
    encodings = ['utf-8', 'ISO-8859-1', 'latin1', 'windows-1252']
    df = None
    for enc in encodings:
        try:
            df = pd.read_csv(scopus_file, encoding=enc, low_memory=False)
            break
        except (UnicodeDecodeError, pd.errors.EmptyDataError):
            continue
    if df is None:
        raise ValueError("Failed to read the file with tested encodings")
        
    # Verificar columnas necesarias
    if 'Authors' not in df.columns or 'Cited by' not in df.columns:
        raise ValueError("Required columns 'Authors' and/or 'Cited by' missing")
        
    # Aseguramos que 'Cited by' sea numérica
    df['Cited by'] = pd.to_numeric(df['Cited by'], errors='coerce').fillna(0)
    
    # Métricas de publicación
    TP = len(df)
    unique_authors = set()
    sole_authored = 0
    multi_authored = 0
    total_authors_in_multi = 0
    
    for _, row in df.iterrows():
        # Se asume que los autores vienen separados por coma y espacio
        authors = str(row['Authors']).split(', ')
        unique_authors.update(authors)
        if len(authors) == 1:
            sole_authored += 1
        else:
            multi_authored += 1
            total_authors_in_multi += len(authors)
    
    NCA = len(unique_authors)
    CI = total_authors_in_multi / multi_authored if multi_authored > 0 else 0  # Índice de Colaboración
    CC = 1 - (sole_authored / TP)  # Coeficiente de Colaboración (una variante)
    
    # Métricas de citación
    TC = df['Cited by'].sum()

    AC = TC / TP if TP > 0 else 0


    NCP = df[df['Cited by'] > 0].shape[0]
    PCP = (NCP / TP) * 100 if TP > 0 else 0
    CCP = TC / NCP if NCP > 0 else 0
    
    # Cálculo de índices:
    citations = df['Cited by'].sort_values(ascending=False).values
    # h-index
    h_index = sum(c >= i+1 for i, c in enumerate(citations))
    # g-index
    cumulative = np.cumsum(citations)
    g_index = 0
    for i, total in enumerate(cumulative):
        if total >= (i+1) ** 2:
            g_index = i + 1
        else:
            break
    # i-index: número de publicaciones con al menos 10, 100, 200 citas
    i10 = (citations >= 10).sum()
    i100 = (citations >= 100).sum()
    i200 = (citations >= 200).sum()
    
    # Impresión de resultados separados en la terminal:
    print("\n=== Publication-related Metrics ===")
    print(f"Total Publications (TP): {TP}")
    print(f"Number of Contributing Authors (NCA): {NCA}")
    print(f"Sole-authored Publications (SA): {sole_authored}")
    print(f"Co-authored Publications (CA): {multi_authored}")
    print(f"Collaboration Index (CI): {round(CI, 2)}")
    print(f"Collaboration Coefficient (CC): {round(CC, 2)}")
    
    print("\n=== Citation-related Metrics ===")
    print(f"Total Citations (TC): {int(TC)}")
    print(f"Average Citation (AC): {(AC)}")
    print(f"Number of Cited Publications (NCP): {NCP}")
    print(f"Proportion of Cited Publications (PCP): {round(PCP, 2)}%")
    print(f"Citations per Cited Publication (CCP): {round(CCP, 2)}")
    print(f"h-index: {h_index}")
    print(f"g-index: {g_index}")
    print(f"i10-index: {int(i10)}")
    print(f"i100-index: {int(i100)}")
    print(f"i200-index: {int(i200)}")
    
    print("\n=== Science Mapping Analysis ===")
    print(" - Citation analysis (Relationships among publications, Most influential publications, Co-citation analysis) - Not implemented")
    print(" - Bibliographic coupling (Relationships among citing publications, Periodical/present themes, Co-word analysis) - Not implemented")
    print(" - Co-authorship analysis (Social interactions, Authors and affiliations) - Not implemented")
    
    # Guardar métricas en CSV
    metrics_dict = {
        "TP": TP,
        "NCA": NCA,
        "SA": sole_authored,
        "CA": multi_authored,
        "CI": round(CI, 2),
        "CC": round(CC, 2),
        "TC": int(TC),
        "NCP": NCP,
        "PCP": round(PCP, 2),
        "CCP": round(CCP, 2),
        "h-index": h_index,
        "g-index": g_index,
        "i10-index": int(i10),
        "i100-index": int(i100),
        "i200-index": int(i200)
    }
    metrics_df = pd.DataFrame(list(metrics_dict.items()), columns=["Metric", "Value"])
    metrics_df.to_csv(os.path.join(output_folder, 'bibliometric_metrics.csv'), index=False)
    
    return metrics_df

import pandas as pd
import numpy as np
import os
import re
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
from itertools import combinations





import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_publications_by_journal(scopus_file, top_n=3):
    try:
        # Leer archivo con codificación automática
        encodings = ['utf-8', 'ISO-8859-1', 'latin1']
        for encoding in encodings:
            try:
                df = pd.read_csv(scopus_file, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        # Identificar columnas de año y revista
        year_cols = ['Year', 'Publication Year', 'Year of Publication']
        journal_cols = ['Source title', 'Journal', 'Publication Name']
        
        year_col = next((col for col in year_cols if col in df.columns), None)
        journal_col = next((col for col in journal_cols if col in df.columns), None)
        
        if year_col is None or journal_col is None:
            raise ValueError("No se encontraron las columnas necesarias (Año y Revista)")
        
        # Convertir año a numérico y filtrar datos válidos
        df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
        df = df.dropna(subset=[year_col, journal_col])
        df[year_col] = df[year_col].astype(int)
        df = df[df[year_col] <= 2024]  # Filtrar hasta el año actual
        
        # Contar artículos por año y revista
        counts = df.groupby([year_col, journal_col]).size().reset_index(name='Publications')
        
        # Obtener el top_n de revistas por año
        top_journals = counts.groupby(year_col).apply(
            lambda x: x.nlargest(top_n, 'Publications')
        ).reset_index(drop=True)
        
        # Pivotear para obtener datos en formato de barras apiladas
        pivot_data = top_journals.pivot(index=year_col, columns=journal_col, values='Publications').fillna(0)
        
        # Crear gráfico
        plt.figure(figsize=(14, 7))
        N=6
        pivot_data.plot(kind='bar', stacked=True, colormap=ListedColormap(generate_colormap(N*N)), edgecolor='black', width=0.8)

        
        # Personalización del gráfico
        plt.title(f'Top {top_n} Journals per Year', fontsize=16, pad=20)
        plt.xlabel('Year', fontsize=14)
        plt.ylabel('Number of Publications', fontsize=14)
        plt.xticks(rotation=45)
        plt.legend(title="Journal", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        
        # Guardar gráfico
        plt.tight_layout()
        plt.savefig('publications_by_journall.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.show()
        
    except Exception as e:
        print(f"Error: {str(e)}")




def plot_publications_by_subject(scopus_file, top_n=5, output_folder='journal_analysis'):
    try:
        os.makedirs(output_folder, exist_ok=True)
        
        encodings = ['utf-8', 'ISO-8859-1', 'latin1', 'windows-1252']
        df = None
        for enc in encodings:
            try:
                df = pd.read_csv(scopus_file, encoding=enc, low_memory=False)
                break
            except (UnicodeDecodeError, pd.errors.EmptyDataError):
                continue
        if df is None:
            raise ValueError("No se pudo leer el archivo con los encodings probados.")

        required_cols = ['Year', 'Source title']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Faltan columnas requeridas: {missing_cols}")

        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df = df.dropna(subset=['Year', 'Source title'])
        df['Year'] = df['Year'].astype(int)
        df = df[df['Year'] <= 2024]

        top_journals = df['Source title'].value_counts().head(top_n).index.tolist()
        df_top = df[df['Source title'].isin(top_journals)]
        journal_counts = df_top.groupby(['Year', 'Source title']).size().unstack(fill_value=0)

        plt.figure(figsize=(14, 8))
        colors = sns.color_palette("tab10", n_colors=top_n)
        hatch_patterns = [""] * (top_n // 2 + 1)
        
        bars = journal_counts.plot(kind='bar', stacked=True, color=colors[:top_n], alpha=0.9)

        for i, bar_container in enumerate(bars.containers):
            for patch in bar_container:
                if i % 2 == 1:  # Aplicar patrón a cada dos colores
                    patch.set_hatch(hatch_patterns[i])

        plt.title(f'Top {top_n} Subjects per Year', fontsize=16, pad=20)
        plt.xlabel("Year", fontsize=14)
        plt.ylabel('Number of Publications', fontsize=14)
        plt.xticks(rotation=45)
        plt.legend(title="Subject", fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.5)

        output_path = os.path.join(output_folder, 'publications_by_journal.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Gráfico guardado en: {output_path}")
        return journal_counts

    except Exception as e:
        print(f"Error en la generación del gráfico: {str(e)}")
        return None

# Uso de la función



def science_mapping_analysis(scopus_file, output_folder='science_mapping'):
    """
    Realiza un análisis de science mapping basado en un archivo Scopus.
    
    Se abordan los siguientes bloques:
    
    1. Citation Analysis:
       - Relaciones entre publicaciones (red de co-citación a partir de la columna "References")
       - Publicaciones más influyentes (ordenadas por "Cited by")
       
    2. Relationships among cited publications:
       - Temas fundacionales (a partir de keywords en "Title" o "Abstract")
       - Bibliographic Coupling (acoplamiento bibliográfico entre pares de documentos que comparten referencias)
       
    3. Relationships among citing publications:
       - Análisis de co-word (red de co-ocurrencia de palabras en "Title" o "Abstract")
       - Temas periódicos o presentes (agrupación por fuente o palabras frecuentes)
       
    4. Co-authorship Analysis:
       - Red de co-autoría (relaciones entre autores extraídas de la columna "Authors")
       - Autores y sus afiliaciones (si existe la columna "Affiliations")
    """
    os.makedirs(output_folder, exist_ok=True)
    
    # Intentar leer el archivo con distintos encodings
    encodings = ['utf-8', 'ISO-8859-1', 'latin1', 'windows-1252']
    df = None
    for enc in encodings:
        try:
            df = pd.read_csv(scopus_file, encoding=enc, low_memory=False)
            break
        except (UnicodeDecodeError, pd.errors.EmptyDataError):
            continue
    if df is None:
        raise ValueError("Failed to read the file with tested encodings")
    
    # --- Sección 1: Citation Analysis ---
    print("\n=== Citation Analysis ===")
    # Publicaciones más influyentes
    if 'Cited by' in df.columns:
        df['Cited by'] = pd.to_numeric(df['Cited by'], errors='coerce').fillna(0)
        influential = df.sort_values('Cited by', ascending=False).head(5)
        print("\nTop 5 Most Influential Publications:")
        if 'Title' in df.columns:
            print(influential[['Title', 'Cited by']].to_string(index=False))
        else:
            print(influential[['Cited by']].to_string(index=False))
    else:
        print("La columna 'Cited by' no está disponible.")
    
    # Construir red de co-citación (suponiendo que existe la columna "References")
    if 'References' in df.columns:
        co_citation_counts = defaultdict(int)
        for idx, row in df.iterrows():
            refs = str(row['References'])
            # Se asume que las referencias están separadas por ";"
            ref_list = [ref.strip() for ref in refs.split(";") if ref.strip() != ""]
            # Para cada par de referencias, incrementar la cuenta
            for ref1, ref2 in combinations(sorted(set(ref_list)), 2):
                co_citation_counts[(ref1, ref2)] += 1
        
        # Crear grafo de co-citación con los pares más frecuentes
        G_cocit = nx.Graph()
        for (ref1, ref2), weight in co_citation_counts.items():
            if weight >= 2:  # umbral para visualizar conexiones relevantes
                G_cocit.add_edge(ref1, ref2, weight=weight)
        
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G_cocit, k=0.5)
        weights = [G_cocit[u][v]['weight'] for u, v in G_cocit.edges()]
        nx.draw(G_cocit, pos, with_labels=True, node_size=500, font_size=8, width=weights)
        plt.title("Co-citation Network")
        cocit_path = os.path.join(output_folder, "co_citation_network.png")
        plt.savefig(cocit_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\nCo-citation network saved to: {cocit_path}")
    else:
        print("La columna 'References' no está disponible para el análisis de co-citación.")
    
    # --- Sección 2: Relationships among cited publications ---
    print("\n=== Relationships among Cited Publications ===")
    # Bibliographic Coupling: se basa en la cantidad de referencias compartidas entre documentos.
    if 'References' in df.columns:
        # Crear un diccionario de paper_id -> conjunto de referencias
        paper_refs = {}
        for idx, row in df.iterrows():
            refs = str(row['References'])
            ref_list = set([ref.strip() for ref in refs.split(";") if ref.strip() != ""])
            paper_refs[idx] = ref_list
        
        # Calcular acoplamiento bibliográfico (para pares de documentos)
        bib_coupling = defaultdict(int)
        paper_ids = list(paper_refs.keys())
        for i in range(len(paper_ids)):
            for j in range(i+1, len(paper_ids)):
                pid1 = paper_ids[i]
                pid2 = paper_ids[j]
                shared = paper_refs[pid1].intersection(paper_refs[pid2])
                if shared:
                    bib_coupling[(pid1, pid2)] = len(shared)
        
        # Extraer los 5 pares con mayor acoplamiento
        if bib_coupling:
            top_bib = sorted(bib_coupling.items(), key=lambda x: x[1], reverse=True)[:5]
            print("\nTop 5 Bibliographic Coupling (Paper IDs and shared references):")
            for pair, count in top_bib:
                print(f"Papers {pair[0]} & {pair[1]}: {count} references shared")
        else:
            print("No se encontró acoplamiento bibliográfico entre documentos.")
    else:
        print("La columna 'References' no está disponible para el análisis de bibliographic coupling.")
    
    # --- Sección 3: Relationships among citing publications ---
    print("\n=== Relationships among Citing Publications ===")
    # Co-word analysis: se extraen palabras de "Title" o "Abstract" y se analiza su co-ocurrencia.
    text_source = None
    if 'Title' in df.columns:
        text_source = df['Title'].fillna('')
    elif 'Abstract' in df.columns:
        text_source = df['Abstract'].fillna('')
    
    if text_source is not None:
        word_cooccurrence = defaultdict(int)
        for text in text_source:
            # Tokenización simple: quitar puntuación y convertir a minúsculas
            words = re.findall(r'\b\w+\b', text.lower())
            words = list(set(words))  # considerar cada palabra una sola vez por documento
            for w1, w2 in combinations(sorted(words), 2):
                word_cooccurrence[(w1, w2)] += 1
        
        # Construir grafo de co-palabras para las 30 conexiones más frecuentes
        top_words = sorted(word_cooccurrence.items(), key=lambda x: x[1], reverse=True)[:30]
        G_coword = nx.Graph()
        for (w1, w2), weight in top_words:
            G_coword.add_edge(w1, w2, weight=weight)
        
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G_coword, k=0.5)
        weights = [G_coword[u][v]['weight'] for u, v in G_coword.edges()]
        nx.draw(G_coword, pos, with_labels=True, node_size=500, font_size=8, width=weights)
        plt.title("Co-word Network")
        coword_path = os.path.join(output_folder, "co_word_network.png")
        plt.savefig(coword_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\nCo-word network saved to: {coword_path}")
    else:
        print("No hay columna 'Title' ni 'Abstract' para el análisis de co-word.")
    
    # --- Sección 4: Co-authorship Analysis ---
    print("\n=== Co-authorship Analysis ===")
    if 'Authors' in df.columns:
        coauthor_graph = nx.Graph()
        for _, row in df.iterrows():
            authors = [a.strip() for a in str(row['Authors']).split(', ') if a.strip() != '']
            # Agregar nodos y aristas para cada par de autores en el documento
            for author in authors:
                coauthor_graph.add_node(author)
            for a1, a2 in combinations(sorted(authors), 2):
                if coauthor_graph.has_edge(a1, a2):
                    coauthor_graph[a1][a2]['weight'] += 1
                else:
                    coauthor_graph.add_edge(a1, a2, weight=1)
        
        plt.figure(figsize=(12, 10))
        pos = nx.spring_layout(coauthor_graph, k=0.3)
        weights = [coauthor_graph[u][v]['weight'] for u, v in coauthor_graph.edges()]
        nx.draw(coauthor_graph, pos, with_labels=True, node_size=300, font_size=8, width=weights)
        plt.title("Co-authorship Network")
        coauth_path = os.path.join(output_folder, "coauthorship_network.png")
        plt.savefig(coauth_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\nCo-authorship network saved to: {coauth_path}")
    else:
        print("La columna 'Authors' no está disponible para el análisis de co-autoría.")
    
    # --- Autores y Afiliaciones ---
    print("\n=== Authors and Affiliations ===")
    if 'Affiliations' in df.columns and 'Authors' in df.columns:
        author_affil = defaultdict(list)
        for _, row in df.iterrows():
            authors = [a.strip() for a in str(row['Authors']).split(', ') if a.strip() != '']
            affils = [aff.strip() for aff in str(row['Affiliations']).split(';') if aff.strip() != '']
            # Se asume correspondencia directa o múltiple; aquí se guarda una lista conjunta
            for author in authors:
                author_affil[author].extend(affils)
        
        # Mostrar algunos ejemplos
        print("Ejemplos de autores y afiliaciones:")
        for author, affils in list(author_affil.items())[:5]:
            print(f"{author}: {', '.join(set(affils))}")
    else:
        print("La columna 'Affiliations' o 'Authors' no está disponible para el análisis de afiliaciones.")
    
    print("\nScience Mapping Analysis completed.")
    
    return

if __name__ == '__main__':
    # Ejemplo de uso:
    file = 'Scopus_VR_ED_full_filters.csv'
    metrica = analyze_bibliometric_metrics(file)
    science_mapping_analysis(file)


# Run analysis


file= 'Scopus_VR_ED_full_filters.csv'
# Ejecutar análisis
top_authors_result = analyze_scopus_authors(file)
production_df, citation_df = analyze_countries(file)
if production_df is not None and citation_df is not None:
    # Save raw data
    output_folder = 'country_results'
    os.makedirs(output_folder, exist_ok=True)
    
    production_df.to_csv(os.path.join(output_folder, 'country_production.csv'), index=False)
    citation_df.to_csv(os.path.join(output_folder, 'country_citations.csv'), index=False)
    plot_publications_by_journal('Scopus_VR_ED_full_filters.csv', top_n=3)
    plot_publications_by_subject('Scopus_VR_ED_full_filters.csv', top_n=3)
    # Generate charts
    plot_country_data(production_df, 'Publications', output_folder)
    plot_country_data(citation_df, 'Citations', output_folder)
    
    # Show console summary
    print("\nTop countries by production:")
    print(production_df.head(10).to_string(index=False))
    
    print("\nTop countries by citations:")
    print(citation_df.head(10).to_string(index=False))
# Usage
results = plot_yearly_publications(file)
metrics_df = analyze_scopus_authors(file, output_folder='publication_related_metrics')

if results is not None:
    print("\nSummary statistics:")
    print(results.describe())
