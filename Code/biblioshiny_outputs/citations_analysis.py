import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_biblioshiny(df,
                     tick_fontsize=16,
                     label_fontsize=18,
                     title_fontsize=20):
    # Datos
    x = np.arange(len(df))
    years          = df['Year'].to_numpy()
    N              = df['N'].to_numpy()
    mean_tc_art    = df['MeanTCperArt'].to_numpy()
    mean_tc_year   = df['MeanTCperYear'].to_numpy()
    citable_years  = df['CitableYears'].to_numpy()

    # Estilo
    plt.style.use('seaborn-white')
    fig, ax1 = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor('white')

    # ————— Barras para N —————
    bar_colors = [plt.get_cmap('Blues')(0.3 + 0.7 * i/len(df))
                  for i in range(len(df))]
    ax1.bar(x, N, color=bar_colors, zorder=2, label='Publications (N)')
    ax1.set_xlabel('Year', fontsize=label_fontsize)
    ax1.set_ylabel('Number of Publications (N)', fontsize=label_fontsize)
    ax1.set_xticks(x)
    ax1.set_xticklabels(years, rotation=45, ha='right', fontsize=tick_fontsize)
    ax1.tick_params(axis='y', labelsize=tick_fontsize)
    ax1.grid(axis='y', linestyle='--', alpha=0.4, zorder=1)

    # Anotaciones encima de las barras
    #for xi, ni in zip(x, N):
    #    ax1.text(xi, ni + max(N)*0.02,
    #             str(ni),
    #             ha='center',
    #             va='bottom',
    #             fontsize=tick_fontsize-8)

    # ————— Líneas para métricas —————
    ax2 = ax1.twinx()
    ax2.set_facecolor((1,1,1,0.0))
    ax2.plot(x, mean_tc_art,   'o-', color='darkgreen',
             label='Mean TC per Art',    linewidth=2, markersize=8)
    ax2.plot(x, mean_tc_year,  's--', color='firebrick',
             label='Mean TC per Year',   linewidth=2, markersize=8)
    ax2.plot(x, citable_years, 'd-.', color='slategray',
             label='Citable Years',       linewidth=2, markersize=8)

    ax2.set_ylabel('Citation Metrics', fontsize=label_fontsize)
    ax2.tick_params(axis='y', labelsize=tick_fontsize)

    # ————— Leyenda y título —————
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    fig.legend(h1+h2, l1+l2,
               loc='upper right',
               bbox_to_anchor=(0.8, 0.9),
               fontsize=tick_fontsize)
    plt.title('Biblioshiny: Publicaciones y Métricas de Citación', fontsize=title_fontsize)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    df = pd.read_excel(
        'Annual_Total_Citation_per_Year_bibliometrix_2025-05-12.xlsx',
        engine='openpyxl', header=1
    )
    df.columns = ['Year','MeanTCperArt','N','MeanTCperYear','CitableYears']
    df = df.dropna(subset=['Year'])
    df['Year'] = df['Year'].astype(int)
    for c in ['MeanTCperArt','N','MeanTCperYear','CitableYears']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.sort_values('Year').reset_index(drop=True)

    plot_biblioshiny(df)

~                                                               
