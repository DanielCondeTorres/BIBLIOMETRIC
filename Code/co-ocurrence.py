import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import itertools

def read_keywords_from_csv(file_path):
    """Read a CSV file and extract keywords from the Author Keywords column"""
    try:
        # First try with comma as delimiter
        df = pd.read_csv(file_path, dtype=str)
        print(f"Columns found with comma delimiter: {', '.join(df.columns)}")
    except:
        try:
            # If that fails, try with tab as delimiter
            df = pd.read_csv(file_path, sep='\t', dtype=str)
            print(f"Columns found with tab delimiter: {', '.join(df.columns)}")
        except:
            try:
                # If that fails, try with semicolon as delimiter
                df = pd.read_csv(file_path, sep=';', dtype=str)
                print(f"Columns found with semicolon delimiter: {', '.join(df.columns)}")
            except Exception as e:
                print(f"Error reading file: {e}")
                raise
    
    # Print all column names to help debug
    print("\nAll column names in the file:")
    for col in df.columns:
        print(f"- {col}")
    
    # Look for author keywords column with case-insensitive match
    keyword_column = None
    for col in df.columns:
        if col.lower() == 'author keywords':
            keyword_column = col
            break
    
    # If not found exactly, look for partial matches
    if not keyword_column:
        for col in df.columns:
            if 'author' in col.lower() and 'keyword' in col.lower():
                keyword_column = col
                break
    
    # If still not found, look for any column with 'keyword' in it
    if not keyword_column:
        for col in df.columns:
            if 'keyword' in col.lower():
                keyword_column = col
                break
    
    # Check if we found a suitable column
    if not keyword_column:
        # Let's check the first 5 rows of data to help debug
        print("\nFirst 5 rows of data:")
        print(df.head())
        raise ValueError("No suitable keyword column found in the file. Please check column names.")
    
    print(f"\nUsing column: {keyword_column}")
    
    # Extract keywords from each paper
    all_paper_keywords = []
    
    # Count papers with and without keywords
    papers_with_keywords = 0
    papers_without_keywords = 0
    
    for _, row in df.iterrows():
        if pd.notna(row[keyword_column]) and str(row[keyword_column]).strip():
            # Split by semicolons (as you mentioned)
            keywords = [k.strip().lower() for k in str(row[keyword_column]).split(';')]
            keywords = [k for k in keywords if k]  # Remove empty strings
            
            if keywords:
                all_paper_keywords.append(keywords)
                papers_with_keywords += 1
            else:
                papers_without_keywords += 1
        else:
            papers_without_keywords += 1
    
    print(f"Papers with keywords: {papers_with_keywords}")
    print(f"Papers without keywords: {papers_without_keywords}")
    
    return all_paper_keywords

def create_cooccurrence_matrix(keywords_lists, top_n=10):
    """Create a co-occurrence matrix from lists of keywords"""
    # Flatten the list and count occurrences
    all_keywords = list(itertools.chain(*keywords_lists))
    keyword_counts = Counter(all_keywords)
    
    # Print the most common keywords
    print("\nMost common keywords:")
    for keyword, count in keyword_counts.most_common(15):
        print(f"{keyword}: {count}")
    
    # Get the top N keywords
    top_keywords = [k for k, _ in keyword_counts.most_common(top_n)]
    
    # Initialize co-occurrence matrix
    cooccurrence_matrix = np.zeros((len(top_keywords), len(top_keywords)))
    
    # Fill the co-occurrence matrix
    for keywords in keywords_lists:
        # Only consider the top keywords
        present_top_keywords = [k for k in keywords if k in top_keywords]
        # For each pair of keywords in this document
        for i, keyword1 in enumerate(present_top_keywords):
            idx1 = top_keywords.index(keyword1)
            for keyword2 in present_top_keywords:
                idx2 = top_keywords.index(keyword2)
                cooccurrence_matrix[idx1, idx2] += 1
    
    # Create a DataFrame for better visualization
    cooccurrence_df = pd.DataFrame(cooccurrence_matrix, index=top_keywords, columns=top_keywords)
    return cooccurrence_df

def visualize_cooccurrence_matrix(cooccurrence_df):
    """Visualize the co-occurrence matrix as a heatmap"""
    plt.figure(figsize=(12, 10))
    
    # Create a mask for the diagonal (self-occurrences)
    mask = np.zeros_like(cooccurrence_df)
    np.fill_diagonal(mask, 1)
    
    # Create the heatmap
    sns.heatmap(
        cooccurrence_df,
        annot=True,
        cmap="YlGnBu",
        mask=mask,  # Mask the diagonal
        fmt=".0f",
        linewidths=0.5,
        cbar_kws={"label": "Co-occurrence frequency"}
    )
    
    plt.title("Keyword Co-occurrence Matrix", fontsize=16)
    plt.tight_layout()
    return plt

def main(file_path):
    """Main function to process the file and generate co-occurrence matrix"""
    # Read keywords from the file
    paper_keywords = read_keywords_from_csv(file_path)
    
    if not paper_keywords:
        print("No keywords found in the file.")
        return None
    
    # Create the co-occurrence matrix
    cooccurrence_df = create_cooccurrence_matrix(paper_keywords, top_n=8)
    
    # Visualize the matrix
    plt = visualize_cooccurrence_matrix(cooccurrence_df)
    plt.savefig('keyword_cooccurrence_matrix.png')
    plt.show()
    
    return cooccurrence_df

# Execute the code with the file path
if __name__ == "__main__":
    # Replace this with your actual CSV file path
    file_path = 'your_file.csv'
    cooccurrence_df = main(file_path)
    print("\nCo-occurrence matrix:")
    print(cooccurrence_df)
