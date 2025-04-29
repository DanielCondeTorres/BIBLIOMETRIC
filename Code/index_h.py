import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

def calculate_h_index(citations):
    """Calculates h-index from a list of citations"""
    citations = sorted(citations, reverse=True)
    h = 0
    for i, c in enumerate(citations):
        if c >= i + 1:
            h = i + 1
        else:
            break
    return h

def process_authors(df):
    """Processes the authors column and calculates metrics"""
    author_citations = defaultdict(list)

    for _, row in df.iterrows():
        if pd.notna(row['Authors']):
            authors = [a.strip() for a in row['Authors'].split(';')]
            citations = row['Cited by']
            for author in authors:
                author_citations[author].append(citations)

    # Calculate metrics for each author
    results = []
    for author, citations in author_citations.items():
        h_index = calculate_h_index(citations)
        results.append({
            'Author': author,
            'H-Index': h_index,
            'Total Publications': len(citations),
            'Total Citations': sum(citations)
        })

    return pd.DataFrame(results)

def visualize_top_authors(top_authors):
    """Generates visualization of the top 10 authors"""
    plt.figure(figsize=(14, 10))
    sns.set_theme(style="whitegrid")

    # Create horizontal bar chart
    ax = sns.barplot(
        x='H-Index',
        y='Author',
        data=top_authors,
        palette='viridis',
        edgecolor='black'
    )

    # Add value labels
    for p in ax.patches:
        ax.annotate(
            f"{int(p.get_width())}",
            (p.get_width(), p.get_y() + p.get_height()/2),
            ha='left', va='center',
            xytext=(7, 0),
            textcoords='offset points',
            fontsize=19,
            fontweight='bold'
        )

    # Customization
    plt.title('Top 10 Authors by H-Index', fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('H-Index', fontsize=22, fontweight='bold')
    plt.ylabel('', fontsize=22)
    plt.xlim(0, top_authors['H-Index'].max() + 3)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)

    # Add a background grid but only for horizontal lines
    ax.yaxis.grid(True, linestyle='--', alpha=0.6)
    ax.xaxis.grid(False)

    sns.despine(left=True)
    plt.tight_layout()
    plt.show()

# Main execution
if __name__ == "__main__":
    # Load data
    try:
        df = pd.read_csv("Scopus_VR_ED_only_2024.csv")
        df['Cited by'] = pd.to_numeric(df['Cited by'], errors='coerce').fillna(0).astype(int)
    except FileNotFoundError:
        print("Error: File not found")
        exit()

    # Process authors
    authors_df = process_authors(df)

    # Get top 10
    top_10 = authors_df.sort_values('H-Index', ascending=False).head(10)

    # Show results
    print("\n🏆 Top 10 Authors by H-Index:")
    print(top_10[['Author', 'H-Index', 'Total Publications', 'Total Citations']]
          .reset_index(drop=True)
          .to_string(index=False))

    # Generate visualization
    visualize_top_authors(top_10)
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                                                                                                                                                              
~                                                                                       
