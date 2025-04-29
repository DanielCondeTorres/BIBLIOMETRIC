import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import cm
from matplotlib.ticker import MaxNLocator

# Set style for a modern, professional look
plt.style.use('seaborn-v0_8-whitegrid')
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = ['Verdana', 'Arial', 'Helvetica', 'DejaVu Sans']

# Data provided
countries = ['China','USA','Spain','United Kingdom','Germany','Australia','Turkey','South Korea','Canada','Greece']
scp = [342, 286, 97, 84, 57, 51, 54, 48, 34, 40]
mcp = [49, 28, 21, 21, 14, 15, 4, 8, 14, 4]

# Calculate totals to display on the chart
totals = [s + m for s, m in zip(scp, mcp)]

# Create custom color palette (blue gradient for SCP and coral for MCP)
scp_color = '#3b7dd8'  # Royal blue
mcp_color = '#ff6b6b'  # Coral red

# Figure and axis configuration with a pleasing aspect ratio - pure white background
fig, ax = plt.subplots(figsize=(14, 10), facecolor='white')
ax.set_facecolor('white')

# Bar positions
x = np.arange(len(countries))
width = 0.65  # Wider bars for better visualization

# Create stacked bars with custom colors
bar1 = ax.bar(x, scp, width, label='SCP', color=scp_color, edgecolor='white', linewidth=0.5)
bar2 = ax.bar(x, mcp, width, bottom=scp, label='MCP', color=mcp_color, edgecolor='white', linewidth=0.5)

# Add labels, title and legend with enhanced styling
ax.set_xlabel('Countries', fontsize=14, fontweight='bold', labelpad=15)
ax.set_ylabel('Cumulative Values', fontsize=14, fontweight='bold', labelpad=15)
ax.set_title('SCP and MCP Values by Country', fontsize=18, fontweight='bold', pad=20)

# Set x-ticks and rotate labels for better readability
ax.set_xticks(x)
ax.set_xticklabels(countries, rotation=45, ha='right', fontsize=12, fontweight='semibold')
ax.tick_params(axis='y', labelsize=12)

# Add a subtle grid only on the y-axis and ensure it's behind the bars
ax.yaxis.grid(True, linestyle='--', alpha=0.6, color='#dddddd')
ax.set_axisbelow(True)

# Force y-axis to use integer values only
ax.yaxis.set_major_locator(MaxNLocator(integer=True))

# Enhance legend appearance
legend = ax.legend(loc='upper right', fontsize=12, frameon=True, framealpha=0.95, 
                   edgecolor='#dddddd', fancybox=True, shadow=True)

# Function to add values on bars with enhanced styling
def add_values_on_bars(bars, offset=0, color='white'):
    for i, bar in enumerate(bars):
        height = bar.get_height()
        if height > 10:  # Only show labels for bars with sufficient height
            ax.annotate('{}'.format(int(height)),
                       xy=(bar.get_x() + bar.get_width() / 2, offset[i] + height/2),
                       xytext=(0, 0),
                       textcoords="offset points",
                       ha='center', va='center',
                       color=color, fontweight='bold', fontsize=11)

# Add total value on top of each stacked bar with enhanced styling
for i, total in enumerate(totals):
    ax.annotate(f'Total: {total}',
               xy=(x[i], total),
               xytext=(0, 7),
               textcoords="offset points",
               ha='center', va='bottom',
               fontweight='bold', fontsize=12,
               bbox=dict(boxstyle="round,pad=0.3", fc='white', ec='#cccccc', alpha=0.8))

# Add values to the bars with custom colors for better visibility
add_values_on_bars(bar1, offset=[0]*len(countries), color='white')
add_values_on_bars(bar2, offset=scp, color='white')

# Add a subtle border to the figure
for spine in ax.spines.values():
    spine.set_edgecolor('#dddddd')
    spine.set_linewidth(1.5)

# Add a caption or source note
fig.text(0.5, 0.01, 'Source: Provided dataset', ha='center', fontsize=10, style='italic', color='#666666')

# Adjust layout for better spacing
plt.tight_layout(rect=[0, 0.03, 1, 0.97])

# Save as high-quality PNG with pure white background
plt.savefig('scp_mcp_by_country.png', dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')

# Show the plot
plt.show()

# Ajustar el diseño para evitar recortes
plt.tight_layout()

# Mostrar el gráfico
plt.show()
