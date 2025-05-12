import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_combined_bar_line(df, x, bar_values, line_values, bar_label, line_label, title,
                           tick_fontsize=10, label_fontsize=12, title_fontsize=14):
    # Convertir a NumPy para evitar errores de indexación multidimensional
    bar_vals = np.array(bar_values)
    line_vals = np.array(line_values)

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Colormap para las barras (Blues con tono más oscuro)
    bar_colors = [plt.get_cmap('Blues')(0.3 + 0.7 * i / len(df)) for i in range(len(df))]
    ax1.bar(x, bar_vals, color=bar_colors, align='center', zorder=1)

    # Línea negra para citas
    ax2 = ax1.twinx()
    ax2.plot(x, line_vals, color='black', linewidth=2, zorder=2)
    ax2.set_ylabel(line_label, fontsize=label_fontsize, color='black')
    ax2.tick_params(axis='y', labelsize=tick_fontsize, labelcolor='black')

    # Línea roja con marcadores sobre las barras
    marker_offset = 5
    adjusted_marker_y = bar_vals - marker_offset
    ax1.plot(x, adjusted_marker_y, 'ro', markersize=8, zorder=4)
    ax1.plot(x, adjusted_marker_y, 'r--', linewidth=1, zorder=3)

    # Números encima de las barras
    for xi, yi in zip(x, bar_vals):
        ax1.annotate(str(yi),
                     xy=(xi, yi + 3),
                     ha='center',
                     va='bottom',
                     fontsize=tick_fontsize-8,
                     zorder=6,
                     annotation_clip=False)

    # Ejes y etiquetas
    ax1.set_xticks(x)
    ax1.set_xticklabels(df['Year'], rotation=45, fontsize=tick_fontsize)
    ax1.set_xlabel('Year', fontsize=label_fontsize)
    ax1.set_ylabel(bar_label, fontsize=label_fontsize)
    ax1.tick_params(axis='y', labelsize=tick_fontsize)

    ax1.set_title(title, fontsize=title_fontsize)

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    # Ruta al CSV exportado de Scopus
    citation_file = 'datos_combinados.csv'

    # Cargar datos
    df_all = pd.read_csv(citation_file)
    df_all['Year'] = pd.to_numeric(df_all['Year'], errors='coerce')
    df_all['Cited by'] = pd.to_numeric(df_all['Cited by'], errors='coerce').fillna(0)
    df_all = df_all.dropna(subset=['Year'])

    # Calcular producción anual = conteo de documentos por año
    production = df_all.groupby('Year').size().reset_index(name='Production')

    # Calcular citas totales por año
    citations = df_all.groupby('Year')['Cited by'].sum().reset_index(name='TotalCitations')

    # Unir producción y citas
    df = pd.merge(production, citations, on='Year').sort_values('Year')

    # Generar gráfico con tamaños de fuente personalizados
    plot_combined_bar_line(
        df=df,
        x=np.arange(len(df)),
        bar_values=df['Production'],
        line_values=df['TotalCitations'],
        bar_label='Annual Production',
        line_label='Total Citations per Year',
        title='Annual Production and Total Citations (desde datos_combinados.csv)',
        tick_fontsize=16,
        label_fontsize=18,
        title_fontsize=20
    )
