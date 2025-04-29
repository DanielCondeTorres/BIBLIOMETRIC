import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set modern style configuration
sns.set_theme(style="whitegrid", palette="husl")
plt.rcParams.update({'font.size': 12, 'axes.titlesize': 16, 'axes.labelsize': 14})

def load_and_process_data(file_path):
    """Load and preprocess citation data"""
    try:
        df = pd.read_csv(file_path)
        df['Cited by'] = pd.to_numeric(df['Cited by'], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        print(f"Data loading error: {str(e)}")
        exit()

def visualize_citations(df):
    """Generate citation visualizations"""
    # Calculate metrics
    total = df.groupby('Year')['Cited by'].sum().reset_index()
    avg = df.groupby('Year')['Cited by'].mean().round(2).reset_index()

    # Create figure
    fig, ax = plt.subplots(2, 1, figsize=(12, 10))

    # Total citations plot
    sns.lineplot(data=total, x='Year', y='Cited by', ax=ax[0],
                marker='o', markersize=8, linewidth=2.5)
    ax[0].set_title('Total Citations by Publication Year', pad=20)
    ax[0].set_ylabel('Total Citations')

    # Average citations plot
    sns.barplot(data=avg, x='Year', y='Cited by', ax=ax[1],
               edgecolor='black', linewidth=1)
    ax[1].set_title('Average Citations per Article', pad=20)
    ax[1].set_ylabel('Average Citations')

    plt.tight_layout()
    plt.show()

    return total, avg

def display_results(total, avg):
    """Display formatted results"""
    print("\n📈 Citation Analysis Report")
    print("="*40)
    print(f"{'Year':<8} | {'Total Citations':<15} | {'Avg Citations':<15}")
    print("-"*40)
    for t, a in zip(total.itertuples(), avg.itertuples()):
        print(f"{t.Year:<8} | {t._2:<15} | {a._2:<15.2f}")

# Main execution
if __name__ == "__main__":
    df = load_and_process_data("Scopus_VR_ED_only_2024.csv")
    total, avg = visualize_citations(df)
    display_results(total, avg)
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
~                                 
