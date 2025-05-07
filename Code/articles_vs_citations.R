# 1. Load required libraries
library(bibliometrix) # for bibliometric data handling
library(dplyr)        # for data manipulation
library(ggplot2)      # for visualization

# 2. Import data from Scopus CSV file
file_path <- "Scopus_VR_ED_full_filters.csv"

# Try to read the file
tryCatch({
  # Convert to bibliometrix format (assuming Scopus file)
  M <- convert2df(file_path, dbsource = "scopus", format = "csv")
  
  # Filter to exclude 2025 publications
  M_filtered <- M %>% filter(PY < 2025)
  
  # Extract citation counts (TC = Times Cited)
  citation_counts <- M_filtered$TC
  
  # Create frequency table for citation distribution
  citation_distribution <- table(citation_counts)
  
  # Convert to dataframe for ggplot
  citation_df <- data.frame(
    citations = as.numeric(names(citation_distribution)),
    articles = as.numeric(citation_distribution)
  )
  
  # Sort by number of citations
  citation_df <- citation_df[order(citation_df$citations), ]
  
  # 3. Create the plot with larger ticks and labels
  p <- ggplot(citation_df, aes(x = citations, y = articles)) +
    geom_bar(stat = "identity", fill = "#8884d8") +
    labs(
      title = "Citation Distribution",
      x = "Number of Citations",
      y = "Number of Articles",
      caption = "Data from Scopus (excluding 2025)"
    ) +
    theme_minimal() +
    theme(
      plot.title = element_text(hjust = 0.5, face = "bold", size = 22),
      axis.title = element_text(face = "bold", size = 20),
      axis.text = element_text(size = 20),
      axis.ticks = element_line(size = 10.2),
      axis.ticks.length = unit(0.2, "cm"),
      panel.grid.major = element_line(size = 0.5)
    )
  
  # Display the plot
  print(p)
  
  # Save the plot if needed
  # ggsave("citation_distribution.png", p, width = 10, height = 6, dpi = 300)
  
  # Also create a table with the data for reference
  print("Citation distribution summary:")
  print(head(citation_df, 20)) # Show first 20 rows
  
  # Find the maximum and minimum citation counts and their frequencies
  max_citation <- max(citation_df$citations)
  min_citation <- min(citation_df$citations)
  
  articles_with_max <- citation_df$articles[which(citation_df$citations == max_citation)]
  articles_with_min <- citation_df$articles[which(citation_df$citations == min_citation)]
  
  # Print the results
  cat("\n=== Citation Analysis ===\n")
  cat("Maximum citations:", max_citation, "- Number of articles with this citation count:", articles_with_max, "\n")
  cat("Minimum citations:", min_citation, "- Number of articles with this citation count:", articles_with_min, "\n")
  
  # Calculate some additional statistics
  total_articles <- sum(citation_df$articles)
  total_citations <- sum(citation_df$citations * citation_df$articles)
  avg_citations <- round(total_citations / total_articles, 2)
  
  # Count articles with zero citations
  zero_citations <- ifelse(min_citation == 0, 
                          articles_with_min, 
                          0)
  
  # Calculate percentage of articles with zero citations
  percent_zero <- round((zero_citations / total_articles) * 100, 2)
  
  # Print additional statistics
  cat("Total number of articles:", total_articles, "\n")
  cat("Total number of citations:", total_citations, "\n")
  cat("Average citations per article:", avg_citations, "\n")
  if(min_citation == 0) {
    cat("Percentage of articles with zero citations:", percent_zero, "%\n")
  }
  
  # Find and display information about the most cited article
  most_cited_article <- M_filtered[which.max(M_filtered$TC), ]
  
  cat("\n=== Most Cited Article ===\n")
  cat("Title:", most_cited_article$TI, "\n")
  cat("Authors:", most_cited_article$AU, "\n")
  cat("Journal:", most_cited_article$SO, "\n")
  cat("Year:", most_cited_article$PY, "\n")
  cat("DOI:", most_cited_article$DI, "\n")
  cat("Number of citations:", most_cited_article$TC, "\n")
  
}, error = function(e) {
  # If there's an error reading the file, create example data
  cat("Error reading the file:", e$message, "\n")
  cat("Generating plot with example data...\n")
  
  # Create example data for a typical citation distribution
  citations <- c(0:20, 25, 30, 35, 45, 60)
  articles <- c(145, 89, 67, 52, 41, 33, 26, 18, 15, 12, 10, 7, 6, 5, 4, 4, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1)
  
  citation_df <- data.frame(citations = citations, articles = articles)
  
  # Create the plot with example data and larger ticks and labels
  p <- ggplot(citation_df, aes(x = citations, y = articles)) +
    geom_bar(stat = "identity", fill = "#8884d8") +
    labs(
      title = "Citation Distribution (Example Data)",
      x = "Number of Citations",
      y = "Number of Articles",
      caption = "Note: Using example data as the original file could not be accessed"
    ) +
    theme_minimal() +
    theme(
      plot.title = element_text(hjust = 0.5, face = "bold", size = 16),
      axis.title = element_text(face = "bold", size = 14),
      axis.text = element_text(size = 12),
      axis.ticks = element_line(size = 1.2),
      axis.ticks.length = unit(0.2, "cm"),
      panel.grid.major = element_line(size = 0.5)
    )
  
  # Display the plot
  print(p)
  
  # Add an informative note
  cat("\nNote: Citation distribution in academic research typically\n")
  cat("follows a power-law or Pareto-like distribution, where most\n")
  cat("articles receive few or no citations, while a small number of\n")
  cat("'star' papers receive a large number of citations.\n")
  cat("This phenomenon is commonly known as the 'Matthew effect' in science.\n")
  
  # Find the maximum and minimum citation counts and their frequencies
  max_citation <- max(citation_df$citations)
  min_citation <- min(citation_df$citations)
  
  articles_with_max <- citation_df$articles[which(citation_df$citations == max_citation)]
  articles_with_min <- citation_df$articles[which(citation_df$citations == min_citation)]
  
  # Print the results
  cat("\n=== Citation Analysis (Example Data) ===\n")
  cat("Maximum citations:", max_citation, "- Number of articles with this citation count:", articles_with_max, "\n")
  cat("Minimum citations:", min_citation, "- Number of articles with this citation count:", articles_with_min, "\n")
  
  # Calculate some additional statistics
  total_articles <- sum(citation_df$articles)
  total_citations <- sum(citation_df$citations * citation_df$articles)
  avg_citations <- round(total_citations / total_articles, 2)
  
  # Count articles with zero citations
  zero_citations <- ifelse(min_citation == 0, 
                          articles_with_min, 
                          0)
  
  # Calculate percentage of articles with zero citations
  percent_zero <- round((zero_citations / total_articles) * 100, 2)
  
  # Print additional statistics
  cat("Total number of articles:", total_articles, "\n")
  cat("Total number of citations:", total_citations, "\n")
  cat("Average citations per article:", avg_citations, "\n")
  if(min_citation == 0) {
    cat("Percentage of articles with zero citations:", percent_zero, "%\n")
  }
  
  # Note about most cited article when using example data
  cat("\n=== Most Cited Article ===\n")
  cat("Note: Since we're using example data, we cannot display the actual most cited article.\n")
  cat("With real data, this section would show details like:\n")
  cat("- Title of the most cited article\n")
  cat("- Authors\n")
  cat("- Journal\n")
  cat("- Year of publication\n")
  cat("- DOI\n")
  cat("- Exact number of citations\n")
})
