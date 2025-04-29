import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def calculate_annual_citation_metrics(df):
    # Filter and calculate metrics
    cited_articles = df[df['Cited by'] > 0].copy()

    annual_metrics = cited_articles.groupby('Year').agg(
        Total_Citations=('Cited by', 'sum'),
        Cited_Articles=('Cited by', 'count')
    ).reset_index()

    annual_metrics['Citations_Per_Article'] = annual_metrics['Total_Citations'] / annual_metrics['Cited_Articles']
    annual_metrics['Year'] = annual_metrics['Year'].astype(str)  # Convert to category

    return annual_metrics

def visualize_metrics(metrics):
    # Create figure and primary axis
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Bar chart on primary axis
    sns.barplot(
        x='Year',
        y='Total_Citations',
        data=metrics,
        color='#3498DB',
        alpha=0.7,
        label='Total Citations',
        ax=ax1
    )

    ax1.set_xlabel('Publication Year', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Total Citations', fontsize=14, fontweight='bold', color='#3498DB')
    ax1.tick_params(axis='y', labelcolor='#3498DB', labelsize=12)
    ax1.tick_params(axis='x', labelsize=12)

    # Create a second Y-axis that shares the same X-axis
    ax2 = ax1.twinx()

    # Line chart on secondary axis
    line = sns.lineplot(
        x='Year',
        y='Citations_Per_Article',
        data=metrics,
        marker='o',
        color='#E74C3C',
        linewidth=3,
        markersize=12,
        label='Citations/Cited Article',
        ax=ax2
    )

    ax2.set_ylabel('Citations per Article', fontsize=14, fontweight='bold', color='#E74C3C')
    ax2.tick_params(axis='y', labelcolor='#E74C3C', labelsize=12)

    # Chart title
    fig.suptitle('Citation Metrics by Publication Year', fontsize=18, fontweight='bold', y=0.98)

    # Add grid to primary chart
    ax1.grid(linestyle=':', alpha=0.7)

    # Get legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()

    # Remove individual legends
    ax1.get_legend().remove() if ax1.get_legend() else None
    ax2.get_legend().remove() if ax2.get_legend() else None

    # Create a combined legend with larger font
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=12)

    # Rotate X-axis labels
    plt.xticks(rotation=45)

    # Adjust spacing
    plt.tight_layout()

    # Show the chart
    plt.show()

# Main execution
df = pd.read_csv("Scopus_VR_ED_only_2024.csv")
df['Cited by'] = pd.to_numeric(df['Cited by'], errors='coerce').fillna(0).astype(int)
annual_metrics = calculate_annual_citation_metrics(df)

print("📊 Detailed Metrics:")
print(annual_metrics.round(2))
print("\n🔍 Statistical Summary:")
print(annual_metrics.describe().round(2))

# Visualize with improved axes
visualize_metrics(annual_metrics)
                                                                                                                                                                        
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                                                                                
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                 
