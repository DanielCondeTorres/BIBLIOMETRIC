import pandas as pd
import plotly.graph_objects as go

# 1. Carga de datos
def load_thematic_data(path):
    df = pd.read_excel(path, sheet_name='Sheet1', header=1)
    df[['from_theme','from_period']] = df['From'].str.split('--', expand=True)
    df[['to_theme'  ,'to_period'  ]] = df['To'  ].str.split('--', expand=True)
    return df

file_path = 'Thematic_Evolution_bibliometrix_2025-04-29.xlsx'
df = load_thematic_data(file_path)

# 2. Definir periodos ordenados
t_periods = sorted(
    pd.unique(df['from_period'].tolist() + df['to_period'].tolist()),
    key=lambda x: int(x.split('-')[0])
)

# 3. Construir etiquetas y posiciones para cada (tema, periodo)
labels = []
keys   = []  # tuplas (theme, period)
node_x = []
node_y = []
for pi, period in enumerate(t_periods):
    temas = sorted(set(
        df.loc[df['from_period'] == period, 'from_theme'].tolist() +
        df.loc[df['to_period']   == period, 'to_theme'  ].tolist()
    ))
    count = len(temas)
    for ti, tema in enumerate(temas):
        labels.append(tema)
        keys.append((tema, period))
        node_x.append(pi / (len(t_periods) - 1))
        node_y.append((ti + 1) / (count + 1))

# Índice de cada nodo por (tema, periodo)
key_to_index = {key: idx for idx, key in enumerate(keys)}

# 4. Mapear flujos a índices usando (tema, periodo)
sources = df.apply(lambda r: key_to_index[(r['from_theme'], r['from_period'])], axis=1)
targets = df.apply(lambda r: key_to_index[(r['to_theme'],   r['to_period'])  ], axis=1)
values  = df['Occurrences']

# 5. Crear el diagrama de Sankey con posiciones fijas
fig = go.Figure(go.Sankey(
    arrangement='fixed',
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color='black', width=0.5),
        label=labels,
        x=node_x,
        y=node_y
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values
    )
))

# 6. Añadir anotaciones de periodos bajo cada columna
annotations = []
for pi, period in enumerate(t_periods):
    annotations.append(dict(
        x=pi/(len(t_periods)-1), y=-0.05,
        xref='paper', yref='paper',
        text=period, showarrow=False,
        font=dict(size=12),
        xanchor='center', yanchor='top'
    ))

fig.update_layout(
    title_text='Evolución Temática por Rangos de Años',
    font_size=14,            # tamaño de letra mayor para etiquetas de nodo
    width=1000,
    height=650,
    margin=dict(b=100),
    annotations=annotations
)

# 7. Mostrar en Jupyter o exportar a HTML
fig.show()
# Para exportar a HTML:
# fig.write_html('sankey_evolucion_tematica.html', auto_open=True)
