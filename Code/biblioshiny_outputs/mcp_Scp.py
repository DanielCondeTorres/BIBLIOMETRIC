import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.ticker import MaxNLocator

# Load the Excel file
file_path = "/mnt/data/scp_mcp_data.xlsx"
df = pd.read_excel(file_path)

# Standardize column names
df.columns = [col.strip() for col in df.columns]
countries = df['Country']
scp = df['SCP']
mcp = df['MCP']
totals = [s + m for s, m in zip(scp, mcp)]

# Plot configuration
plt.style.use('seaborn-v0_8-whitegrid')
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = ['Verdana', 'Arial', 'Helvetica', 'DejaVu Sans']

scp_color = '#3b7dd8'
mcp_color = '#ff6b6b'

fig, ax = plt.subplots(figsize=(14, 10), facecolor='white')
ax.set_facecolor('white')

x = np.arange(len(countries))
width = 0.65

bar1 = ax.bar(x, scp, width, label='SCP', color=scp_color, edgecolor='white', linewidth=0.5)
bar2 = ax.bar(x, mcp, width, bottom=scp, label='MCP', color=mcp_color, edgecolor='white', linewidth=0.5)

ax.set_xlabel('Countries', fontsize=16, fontweight='bold', labelpad=15)
ax.set_ylabel('Number of Articles', fontsize=16, fontweight='bold', labelpad=15)
ax.set_title('SCP and MCP Distribution by Country', fontsize=20, fontweight='bold', pad=20)

ax.set_xticks(x)
ax.set_xticklabels(countries, rotation=45, ha='right', fontsize=14, fontweight='semibold')
ax.tick_params(axis='y', labelsize=14)
ax.yaxis.grid(True, linestyle='--', alpha=0.6, color='#dddddd')
ax.set_axisbelow(True)
ax.yaxis.set_major_locator(MaxNLocator(integer=True))

legend = ax.legend(loc='upper right', fontsize=13, frameon=True, framealpha=0.95, 
                   edgecolor='#dddddd', fancybox=True, shadow=True)

def add_values_on_bars(bars, offset=0, color='white'):
    for i, bar in enumerate(bars):
        height = bar.get_height()
        if height > 10:
            ax.annotate(f"{int(height)}",
                        xy=(bar.get_x() + bar.get_width() / 2, offset[i] + height/2),
                        xytext=(0, 0),
                        textcoords="offset points",
                        ha='center', va='center',
                        color=color, fontweight='bold', fontsize=12)

for i, total in enumerate(totals):
    ax.annotate(f'Total: {total}',
                xy=(x[i], total),
                xytext=(0, 7),
                textcoords="offset points",
                ha='center', va='bottom',
                fontweight='bold', fontsize=13,
                bbox=dict(boxstyle="round,pad=0.3", fc='white', ec='#cccccc', alpha=0.8))

add_values_on_bars(bar1, offset=[0]*len(countries), color='white')
add_values_on_bars(bar2, offset=scp, color='white')

for spine in ax.spines.values():
    spine.set_edgecolor('#dddddd')
    spine.set_linewidth(1.5)

fig.text(0.5, 0.01, 'Source: Provided dataset', ha='center', fontsize=11, style='italic', color='#666666')

plt.tight_layout(rect=[0, 0.03, 1, 0.97])
plt.show()
