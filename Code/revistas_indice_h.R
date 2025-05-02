# Load required libraries
library(bibliometrix)
library(dplyr)
library(ggplot2)

# Set working directory if needed
# setwd("your/path/here")

# 1. Import and preprocess data
# Make sure your Scopus export file is in the working directory
file_path <- "Scopus_VR_ED_full_filters.csv"

# Try to import the data with error handling
tryCatch({
  df <- convert2df(file_path, dbsource = "scopus", format = "csv")
  
  # Print summary information about the dataset
  cat("\nDataset successfully loaded!\n")
  cat("Number of documents:", nrow(df), "\n")
  cat("Number of columns:", ncol(df), "\n\n")
  
}, error = function(e) {
  cat("Error importing data:", e$message, "\n")
  cat("Trying alternative import method...\n")
  
  # If convert2df fails, try reading directly with read.csv
  df <- read.csv(file_path, stringsAsFactors = FALSE, check.names = FALSE)
  cat("Data imported using read.csv instead. Some bibliometrix functions may be limited.\n")
})

# First filter out publications from 2025
year_column <- NULL
if("PY" %in% names(df)) {
  year_column <- "PY"
} else if("Year" %in% names(df)) {
  year_column <- "Year"
} else {
  # Look for any column that might contain year information
  year_cols <- grep("year|date|PY", names(df), ignore.case = TRUE)
  if(length(year_cols) > 0) {
    year_column <- names(df)[year_cols[1]]
  }
}

if(!is.null(year_column)) {
  # Convert year to numeric and filter out 2025
  df[[year_column]] <- as.numeric(as.character(df[[year_column]]))
  df_filtered <- df[df[[year_column]] != 2025, ]
  cat("Excluded publications from 2025. Dataset now has", nrow(df_filtered), "documents.\n")
  
  # Replace df with the filtered version
  df <- df_filtered
} else {
  cat("No year column found. Could not filter by year.\n")
}

# Create a bibliometric object
results <- biblioAnalysis(df)
summary_results <- summary(results)

# 2. Analyze top affiliations
# Extract and analyze affiliations - handle different column naming conventions
# First, check what columns are available
print("Available columns in the dataset:")
print(names(df))

# Check if affiliation columns exist and use them accordingly
if("AU_UN" %in% names(df)) {
  # If AU_UN exists, use it directly
  affiliations <- df$AU_UN
} else if("AU1_CO" %in% names(df)) {
  # Some Scopus exports use AU1_CO, AU1_UN format
  affiliations <- df$AU1_UN
} else if("Affiliations" %in% names(df)) {
  # Sometimes affiliations are under this name
  affiliations <- df$Affiliations
} else {
  # If none of the expected columns exist, try to find a column with "affiliation" in its name
  affiliation_cols <- grep("affil|univ|instit", names(df), ignore.case = TRUE)
  if(length(affiliation_cols) > 0) {
    affiliations <- df[[affiliation_cols[1]]]
  } else {
    # If no affiliation column found
    cat("No affiliation column found in the dataset. Column names are:", names(df), "\n")
    affiliations <- character(0)
  }
}

# Process affiliations if they exist
if(length(affiliations) > 0) {
  # Split and count affiliations
  all_affiliations <- unlist(strsplit(as.character(affiliations), ";"))
  all_affiliations <- trimws(all_affiliations)
  all_affiliations <- all_affiliations[all_affiliations != ""]
  affiliation_counts <- table(all_affiliations)
  top_affiliations <- sort(affiliation_counts, decreasing = TRUE)[1:min(20, length(affiliation_counts))]
} else {
  top_affiliations <- character(0)
}

# Create a data frame for plotting
if(length(top_affiliations) > 0) {
  top_aff_df <- data.frame(
    Affiliation = names(top_affiliations),
    Publications = as.numeric(top_affiliations)
  )
} else {
  top_aff_df <- data.frame(Affiliation = character(0), Publications = numeric(0))
}

# 3. Analyze top journals
# Extract and count journals
journals <- df %>%
  select(SO) %>%
  filter(!is.na(SO))

journal_counts <- table(journals$SO)
top_journals <- sort(journal_counts, decreasing = TRUE)[1:min(20, length(journal_counts))]

# Create a data frame for plotting
top_journal_df <- data.frame(
  Journal = names(top_journals),
  Publications = as.numeric(top_journals)
)

# 4. Define function to calculate h-index for journals
calculate_journal_h_index <- function(df) {
  # Get list of unique journals
  journals <- unique(df$SO)
  journal_h_index <- data.frame(Journal = character(), H_Index = numeric(), stringsAsFactors = FALSE)
  
  # Check if citation column exists
  citation_col <- NULL
  if("TC" %in% names(df)) {
    citation_col <- "TC"
  } else if("Citations" %in% names(df)) {
    citation_col <- "Citations"
  } else {
    # Look for any column containing citation information
    citation_cols <- grep("cit", names(df), ignore.case = TRUE)
    if(length(citation_cols) > 0) {
      citation_col <- names(df)[citation_cols[1]]
    }
  }
  
  # If citation column exists
  if(!is.null(citation_col)) {
    # For each journal
    for (journal in journals) {
      # Get all articles from this journal
      journal_articles <- df[df$SO == journal, ]
      
      # Get citation counts for these articles
      citations <- suppressWarnings(as.numeric(journal_articles[[citation_col]]))
      citations <- citations[!is.na(citations)]
      
      if(length(citations) > 0) {
        # Calculate h-index
        sorted_citations <- sort(citations, decreasing = TRUE)
        h_index <- sum(sorted_citations >= seq_along(sorted_citations))
      } else {
        h_index <- 0
      }
      
      # Add to dataframe
      journal_h_index <- rbind(journal_h_index, data.frame(Journal = journal, H_Index = h_index))
    }
    
    # Sort by h-index
    journal_h_index <- journal_h_index[order(journal_h_index$H_Index, decreasing = TRUE), ]
  } else {
    cat("No citation column found in the dataset. Cannot calculate h-index.\n")
  }
  
  return(journal_h_index)
}

# 5. Define function to create journal h-index table
create_journal_h_table <- function(journal_h_index, top_n = 20) {
  # Merge with publication counts if available
  if(exists("top_journal_df")) {
    merged_table <- merge(journal_h_index, top_journal_df, by.x = "Journal", by.y = "Journal", all.x = TRUE)
    names(merged_table)[names(merged_table) == "Publications"] <- "Num_Publications"
    merged_table$Num_Publications[is.na(merged_table$Num_Publications)] <- 0
  } else {
    # Count publications per journal manually
    journal_counts <- table(df$SO)
    merged_table <- cbind(journal_h_index, 
                         Num_Publications = as.vector(journal_counts[match(journal_h_index$Journal, names(journal_counts))]))
  }
  
  # Sort by H-Index
  merged_table <- merged_table[order(merged_table$H_Index, decreasing = TRUE), ]
  
  # Select top N journals
  top_table <- head(merged_table, top_n)
  
  # Print the table
  cat("\n=== TOP", top_n, "JOURNALS WITH H-INDEX AND PUBLICATION COUNT ===\n")
  print(top_table)
  
  # Save as CSV
  write.csv(merged_table, "journals_h_index_and_publications.csv", row.names = FALSE)
  
  return(top_table)
}

# 6. Calculate journal h-indices and create table
journal_h_index <- calculate_journal_h_index(df)
top_journals_h_index <- head(journal_h_index, 20)

# Create and display the combined journal h-index table
journal_h_table <- create_journal_h_table(journal_h_index)

# 7. Create visualizations
# Plot top affiliations
if(nrow(top_aff_df) > 0) {
  ggplot(top_aff_df[1:min(10, nrow(top_aff_df)),], aes(x = reorder(Affiliation, Publications), y = Publications)) +
    geom_bar(stat = "identity", fill = "skyblue") +
    coord_flip() +
    theme_minimal() +
    labs(title = "Top 10 Affiliations by Number of Publications",
         x = "Affiliation",
         y = "Number of Publications")
}

# Plot top journals
ggplot(top_journal_df[1:min(10, nrow(top_journal_df)),], aes(x = reorder(Journal, Publications), y = Publications)) +
  geom_bar(stat = "identity", fill = "lightgreen") +
  coord_flip() +
  theme_minimal() +
  labs(title = "Top 10 Journals by Number of Publications",
       x = "Journal",
       y = "Number of Publications")

# Plot h-index of top journals
ggplot(top_journals_h_index[1:min(10, nrow(top_journals_h_index)),], aes(x = reorder(Journal, H_Index), y = H_Index)) +
  geom_bar(stat = "identity", fill = "salmon") +
  coord_flip() +
  theme_minimal() +
  labs(title = "Top 10 Journals by H-Index",
       x = "Journal",
       y = "H-Index")

# Create a visualization of the journal h-index table
if(nrow(journal_h_table) > 0) {
  # Select top 15 for better visualization
  plot_data <- head(journal_h_table, 15)
  
  # Create a plot that shows both h-index and publication count
  h_index_plot <- ggplot(plot_data, aes(x = reorder(Journal, H_Index))) +
    geom_bar(aes(y = H_Index), stat = "identity", fill = "salmon", alpha = 0.7) +
    geom_text(aes(y = H_Index + 0.5, label = H_Index), size = 3) +
    geom_bar(aes(y = Num_Publications/max(Num_Publications) * max(H_Index) * 0.8), 
             stat = "identity", fill = "skyblue", alpha = 0.5) +
    scale_y_continuous(
      name = "H-Index",
      sec.axis = sec_axis(~./max(plot_data$H_Index) * max(plot_data$Num_Publications) * 1.25, 
                         name = "Number of Publications")
    ) +
    coord_flip() +
    theme_minimal() +
    labs(title = "Top Journals: H-Index (red) and Publication Count (blue)",
         x = "Journal") +
    theme(axis.text.y = element_text(size = 8))
  
  # Print the plot
  print(h_index_plot)
  
  # Save the plot
  ggsave("journal_h_index_and_publications.png", h_index_plot, width = 12, height = 8, dpi = 300)
}

# 8. Save results to files
write.csv(top_aff_df, "top_affiliations.csv", row.names = FALSE)
write.csv(top_journal_df, "top_journals.csv", row.names = FALSE)
write.csv(top_journals_h_index, "journal_h_index.csv", row.names = FALSE)

# 9. Additional bibliometric analyses
# Country collaboration - adjust for possible different column names
country_field <- NULL
if("AU_CO" %in% names(df)) {
  country_field <- "AU_CO"
} else if("Countries" %in% names(df)) {
  country_field <- "Countries"
} else {
  country_cols <- grep("countr", names(df), ignore.case = TRUE)
  if(length(country_cols) > 0) {
    country_field <- names(df)[country_cols[1]]
  }
}

if(!is.null(country_field)) {
  tryCatch({
    country_collab <- metaTagExtraction(df, Field = country_field, sep = ";")
    country_matrix <- biblioNetwork(country_collab, analysis = "collaboration", network = "countries")
    # You can visualize this with networkPlot if desired
  }, error = function(e) {
    cat("Error in country collaboration analysis:", e$message, "\n")
  })
} else {
  cat("No country column found for collaboration analysis.\n")
}

# Keyword co-occurrence - adjust for possible different column names
keyword_field <- NULL
if("DE" %in% names(df)) {
  keyword_field <- "DE"
} else if("ID" %in% names(df)) {
  keyword_field <- "ID"
} else if("Keywords" %in% names(df)) {
  keyword_field <- "Keywords"
} else {
  keyword_cols <- grep("keyword", names(df), ignore.case = TRUE)
  if(length(keyword_cols) > 0) {
    keyword_field <- names(df)[keyword_cols[1]]
  }
}

if(!is.null(keyword_field)) {
  tryCatch({
    keyword_co <- metaTagExtraction(df, Field = keyword_field, sep = ";")
    keyword_matrix <- biblioNetwork(keyword_co, analysis = "co-occurrences", network = "keywords")
  }, error = function(e) {
    cat("Error in keyword co-occurrence analysis:", e$message, "\n")
  })
} else {
  cat("No keyword column found for co-occurrence analysis.\n")
}

# Print summary of the bibliometric analysis
cat("\n=== SUMMARY OF BIBLIOMETRIC ANALYSIS ===\n")
print(summary_results)











# Print summary of the bibliometric analysis
cat("\n=== SUMMARY OF BIBLIOMETRIC ANALYSIS ===\n")
print(summary_results)
# Load required libraries
library(bibliometrix)
library(dplyr)
library(ggplot2)

# Set working directory if needed
# setwd("your/path/here")

# 1. Import and preprocess data
# Make sure your Scopus export file is in the working directory
file_path <- "Scopus_VR_ED_full_filters.csv"

# Try to import the data with error handling
tryCatch({
  df <- convert2df(file_path, dbsource = "scopus", format = "csv")
  
  # Print summary information about the dataset
  cat("\nDataset successfully loaded!\n")
  cat("Number of documents:", nrow(df), "\n")
  cat("Number of columns:", ncol(df), "\n\n")
  
}, error = function(e) {
  cat("Error importing data:", e$message, "\n")
  cat("Trying alternative import method...\n")
  
  # If convert2df fails, try reading directly with read.csv
  df <- read.csv(file_path, stringsAsFactors = FALSE, check.names = FALSE)
  cat("Data imported using read.csv instead. Some bibliometrix functions may be limited.\n")
})

# First filter out publications from 2025
year_column <- NULL
if("PY" %in% names(df)) {
  year_column <- "PY"
} else if("Year" %in% names(df)) {
  year_column <- "Year"
} else {
  # Look for any column that might contain year information
  year_cols <- grep("year|date|PY", names(df), ignore.case = TRUE)
  if(length(year_cols) > 0) {
    year_column <- names(df)[year_cols[1]]
  }
}

if(!is.null(year_column)) {
  # Convert year to numeric and filter out 2025
  df[[year_column]] <- as.numeric(as.character(df[[year_column]]))
  df_filtered <- df[df[[year_column]] != 2025, ]
  cat("Excluded publications from 2025. Dataset now has", nrow(df_filtered), "documents.\n")
  
  # Replace df with the filtered version
  df <- df_filtered
} else {
  cat("No year column found. Could not filter by year.\n")
}

# Create a bibliometric object
results <- biblioAnalysis(df)
summary_results <- summary(results)

# 2. Analyze top affiliations
# Extract and analyze affiliations - handle different column naming conventions
# First, check what columns are available
print("Available columns in the dataset:")
print(names(df))

# Check if affiliation columns exist and use them accordingly
if("AU_UN" %in% names(df)) {
  # If AU_UN exists, use it directly
  affiliations <- df$AU_UN
} else if("AU1_CO" %in% names(df)) {
  # Some Scopus exports use AU1_CO, AU1_UN format
  affiliations <- df$AU1_UN
} else if("Affiliations" %in% names(df)) {
  # Sometimes affiliations are under this name
  affiliations <- df$Affiliations
} else {
  # If none of the expected columns exist, try to find a column with "affiliation" in its name
  affiliation_cols <- grep("affil|univ|instit", names(df), ignore.case = TRUE)
  if(length(affiliation_cols) > 0) {
    affiliations <- df[[affiliation_cols[1]]]
  } else {
    # If no affiliation column found
    cat("No affiliation column found in the dataset. Column names are:", names(df), "\n")
    affiliations <- character(0)
  }
}

# Process affiliations if they exist
if(length(affiliations) > 0) {
  # Split and count affiliations
  all_affiliations <- unlist(strsplit(as.character(affiliations), ";"))
  all_affiliations <- trimws(all_affiliations)
  all_affiliations <- all_affiliations[all_affiliations != ""]
  affiliation_counts <- table(all_affiliations)
  top_affiliations <- sort(affiliation_counts, decreasing = TRUE)[1:min(20, length(affiliation_counts))]
} else {
  top_affiliations <- character(0)
}

# Create a data frame for plotting
if(length(top_affiliations) > 0) {
  top_aff_df <- data.frame(
    Affiliation = names(top_affiliations),
    Publications = as.numeric(top_affiliations)
  )
} else {
  top_aff_df <- data.frame(Affiliation = character(0), Publications = numeric(0))
}

# 3. Analyze top journals
# Extract and count journals
journals <- df %>%
  select(SO) %>%
  filter(!is.na(SO))

journal_counts <- table(journals$SO)
top_journals <- sort(journal_counts, decreasing = TRUE)[1:min(20, length(journal_counts))]

# Create a data frame for plotting
top_journal_df <- data.frame(
  Journal = names(top_journals),
  Publications = as.numeric(top_journals)
)

# 4. Define function to calculate h-index for journals
calculate_journal_h_index <- function(df) {
  # Get list of unique journals
  journals <- unique(df$SO)
  journal_h_index <- data.frame(Journal = character(), H_Index = numeric(), stringsAsFactors = FALSE)
  
  # Check if citation column exists
  citation_col <- NULL
  if("TC" %in% names(df)) {
    citation_col <- "TC"
  } else if("Citations" %in% names(df)) {
    citation_col <- "Citations"
  } else {
    # Look for any column containing citation information
    citation_cols <- grep("cit", names(df), ignore.case = TRUE)
    if(length(citation_cols) > 0) {
      citation_col <- names(df)[citation_cols[1]]
    }
  }
  
  # If citation column exists
  if(!is.null(citation_col)) {
    # For each journal
    for (journal in journals) {
      # Get all articles from this journal
      journal_articles <- df[df$SO == journal, ]
      
      # Get citation counts for these articles
      citations <- suppressWarnings(as.numeric(journal_articles[[citation_col]]))
      citations <- citations[!is.na(citations)]
      
      if(length(citations) > 0) {
        # Calculate h-index
        sorted_citations <- sort(citations, decreasing = TRUE)
        h_index <- sum(sorted_citations >= seq_along(sorted_citations))
      } else {
        h_index <- 0
      }
      
      # Add to dataframe
      journal_h_index <- rbind(journal_h_index, data.frame(Journal = journal, H_Index = h_index))
    }
    
    # Sort by h-index
    journal_h_index <- journal_h_index[order(journal_h_index$H_Index, decreasing = TRUE), ]
  } else {
    cat("No citation column found in the dataset. Cannot calculate h-index.\n")
  }
  
  return(journal_h_index)
}

# 5. Define function to create journal h-index table
create_journal_h_table <- function(journal_h_index, top_n = 20) {
  # Merge with publication counts if available
  if(exists("top_journal_df")) {
    merged_table <- merge(journal_h_index, top_journal_df, by.x = "Journal", by.y = "Journal", all.x = TRUE)
    names(merged_table)[names(merged_table) == "Publications"] <- "Num_Publications"
    merged_table$Num_Publications[is.na(merged_table$Num_Publications)] <- 0
  } else {
    # Count publications per journal manually
    journal_counts <- table(df$SO)
    merged_table <- cbind(journal_h_index, 
                         Num_Publications = as.vector(journal_counts[match(journal_h_index$Journal, names(journal_counts))]))
  }
  
  # Sort by H-Index
  merged_table <- merged_table[order(merged_table$H_Index, decreasing = TRUE), ]
  
  # Select top N journals
  top_table <- head(merged_table, top_n)
  
  # Print the table
  cat("\n=== TOP", top_n, "JOURNALS WITH H-INDEX AND PUBLICATION COUNT ===\n")
  print(top_table)
  
  # Save as CSV
  write.csv(merged_table, "journals_h_index_and_publications.csv", row.names = FALSE)
  
  return(top_table)
}

# 6. Calculate journal h-indices and create table
journal_h_index <- calculate_journal_h_index(df)
top_journals_h_index <- head(journal_h_index, 20)

# Create and display the combined journal h-index table
journal_h_table <- create_journal_h_table(journal_h_index)

# 7. Create visualizations
# Plot top affiliations
if(nrow(top_aff_df) > 0) {
  ggplot(top_aff_df[1:min(10, nrow(top_aff_df)),], aes(x = reorder(Affiliation, Publications), y = Publications)) +
    geom_bar(stat = "identity", fill = "skyblue") +
    coord_flip() +
    theme_minimal() +
    labs(title = "Top 10 Affiliations by Number of Publications",
         x = "Affiliation",
         y = "Number of Publications")
}

# Plot top journals
ggplot(top_journal_df[1:min(10, nrow(top_journal_df)),], aes(x = reorder(Journal, Publications), y = Publications)) +
  geom_bar(stat = "identity", fill = "lightgreen") +
  coord_flip() +
  theme_minimal() +
  labs(title = "Top 10 Journals by Number of Publications",
       x = "Journal",
       y = "Number of Publications")

# Plot h-index of top journals
ggplot(top_journals_h_index[1:min(10, nrow(top_journals_h_index)),], aes(x = reorder(Journal, H_Index), y = H_Index)) +
  geom_bar(stat = "identity", fill = "salmon") +
  coord_flip() +
  theme_minimal() +
  labs(title = "Top 10 Journals by H-Index",
       x = "Journal",
       y = "H-Index")

# Create a visualization of the journal h-index table
if(nrow(journal_h_table) > 0) {
  # Select top 15 for better visualization
  plot_data <- head(journal_h_table, 15)
  
  # Create a plot that shows both h-index and publication count
  h_index_plot <- ggplot(plot_data, aes(x = reorder(Journal, H_Index))) +
    geom_bar(aes(y = H_Index), stat = "identity", fill = "salmon", alpha = 0.7) +
    geom_text(aes(y = H_Index + 0.5, label = H_Index), size = 3) +
    geom_bar(aes(y = Num_Publications/max(Num_Publications) * max(H_Index) * 0.8), 
             stat = "identity", fill = "skyblue", alpha = 0.5) +
    scale_y_continuous(
      name = "H-Index",
      sec.axis = sec_axis(~./max(plot_data$H_Index) * max(plot_data$Num_Publications) * 1.25, 
                         name = "Number of Publications")
    ) +
    coord_flip() +
    theme_minimal() +
    labs(title = "Top Journals: H-Index (red) and Publication Count (blue)",
         x = "Journal") +
    theme(axis.text.y = element_text(size = 8))
  
  # Print the plot
  print(h_index_plot)
  
  # Save the plot
  ggsave("journal_h_index_and_publications.png", h_index_plot, width = 12, height = 8, dpi = 300)
}

# 8. Save results to files
write.csv(top_aff_df, "top_affiliations.csv", row.names = FALSE)
write.csv(top_journal_df, "top_journals.csv", row.names = FALSE)
write.csv(top_journals_h_index, "journal_h_index.csv", row.names = FALSE)

# 9. Additional bibliometric analyses
# Country collaboration - adjust for possible different column names
country_field <- NULL
if("AU_CO" %in% names(df)) {
  country_field <- "AU_CO"
} else if("Countries" %in% names(df)) {
  country_field <- "Countries"
} else {
  country_cols <- grep("countr", names(df), ignore.case = TRUE)
  if(length(country_cols) > 0) {
    country_field <- names(df)[country_cols[1]]
  }
}

if(!is.null(country_field)) {
  tryCatch({
    country_collab <- metaTagExtraction(df, Field = country_field, sep = ";")
    country_matrix <- biblioNetwork(country_collab, analysis = "collaboration", network = "countries")
    # You can visualize this with networkPlot if desired
  }, error = function(e) {
    cat("Error in country collaboration analysis:", e$message, "\n")
  })
} else {
  cat("No country column found for collaboration analysis.\n")
}

# Keyword co-occurrence - adjust for possible different column names
keyword_field <- NULL
if("DE" %in% names(df)) {
  keyword_field <- "DE"
} else if("ID" %in% names(df)) {
  keyword_field <- "ID"
} else if("Keywords" %in% names(df)) {
  keyword_field <- "Keywords"
} else {
  keyword_cols <- grep("keyword", names(df), ignore.case = TRUE)
  if(length(keyword_cols) > 0) {
    keyword_field <- names(df)[keyword_cols[1]]
  }
}

if(!is.null(keyword_field)) {
  tryCatch({
    keyword_co <- metaTagExtraction(df, Field = keyword_field, sep = ";")
    keyword_matrix <- biblioNetwork(keyword_co, analysis = "co-occurrences", network = "keywords")
  }, error = function(e) {
    cat("Error in keyword co-occurrence analysis:", e$message, "\n")
  })
} else {
  cat("No keyword column found for co-occurrence analysis.\n")
}

# 10. Analyze Total Citations per Country (with options for counting method)
cat("\n=== ANALYZING TOTAL CITATIONS PER COUNTRY ===\n")

# Find country columns - look for both general and corresponding author countries
country_field <- NULL
corresponding_country_field <- NULL

# Check for regular country field
if("AU_CO" %in% names(df)) {
  country_field <- "AU_CO"
} else if("Countries" %in% names(df)) {
  country_field <- "Countries"
} else {
  country_cols <- grep("countr", names(df), ignore.case = TRUE)
  if(length(country_cols) > 0) {
    country_field <- names(df)[country_cols[1]]
  }
}

# Check for corresponding author country field
if("CO_CO" %in% names(df)) {
  corresponding_country_field <- "CO_CO"
} else if("RP_CO" %in% names(df)) {
  corresponding_country_field <- "RP_CO"
} else {
  corresponding_cols <- grep("correspond.*countr|RP.*CO", names(df), ignore.case = TRUE)
  if(length(corresponding_cols) > 0) {
    corresponding_country_field <- names(df)[corresponding_cols[1]]
  }
}

# Find citation column
citation_col <- NULL
if("TC" %in% names(df)) {
  citation_col <- "TC"
} else if("Citations" %in% names(df)) {
  citation_col <- "Citations"
} else {
  citation_cols <- grep("cit", names(df), ignore.case = TRUE)
  if(length(citation_cols) > 0) {
    citation_col <- names(df)[citation_cols[1]]
  }
}

# Function to calculate citations per country based on specified counting method
calculate_country_citations <- function(df, country_col, citation_col, method="full") {
  # Ensure we have the necessary columns
  if(is.null(country_col) || is.null(citation_col)) {
    return(NULL)
  }
  
  # Extract countries and ensure they're in a usable format
  countries <- df[[country_col]]
  countries <- as.character(countries)
  
  # Extract citations and ensure they're numeric
  citations <- suppressWarnings(as.numeric(df[[citation_col]]))
  citations[is.na(citations)] <- 0
  
  # Create a dataframe with countries and citations
  country_citations <- data.frame(Country = countries, Citations = citations)
  
  # Initialize vectors for results
  all_countries <- c()
  all_citations <- c()
  
  if(method == "full") {
    # Full counting: each country gets full credit for the paper's citations
    for(i in 1:nrow(country_citations)) {
      if(!is.na(country_citations$Country[i])) {
        countries_list <- unlist(strsplit(country_citations$Country[i], ";"))
        countries_list <- trimws(countries_list)
        
        # For each country in the list, add the citation count
        for(country in countries_list) {
          if(country != "") {
            all_countries <- c(all_countries, country)
            all_citations <- c(all_citations, country_citations$Citations[i])
          }
        }
      }
    }
  } else if(method == "fractional") {
    # Fractional counting: citations are divided among countries
    for(i in 1:nrow(country_citations)) {
      if(!is.na(country_citations$Country[i])) {
        countries_list <- unlist(strsplit(country_citations$Country[i], ";"))
        countries_list <- trimws(countries_list)
        countries_list <- countries_list[countries_list != ""]
        
        # Skip if no valid countries
        if(length(countries_list) == 0) next
        
        # Divide citations among countries
        fraction <- country_citations$Citations[i] / length(countries_list)
        
        # For each country in the list, add the fractional citation count
        for(country in countries_list) {
          all_countries <- c(all_countries, country)
          all_citations <- c(all_citations, fraction)
        }
      }
    }
  }
  
  # Create a new dataframe with the expanded data
  expanded_data <- data.frame(Country = all_countries, Citations = all_citations)
  
  # Sum citations by country
  TCperCountries <- aggregate(Citations ~ Country, data = expanded_data, sum)
  
  # Sort by citations in descending order
  TCperCountries <- TCperCountries[order(TCperCountries$Citations, decreasing = TRUE), ]
  
  return(TCperCountries)
}

# Calculate citations for all countries (full counting method)
if(!is.null(country_field) && !is.null(citation_col)) {
  tryCatch({
    # Calculate using full counting (every country gets full credit)
    TCperCountries_full <- calculate_country_citations(df, country_field, citation_col, "full")
    
    # Calculate using fractional counting (citations divided among countries)
    TCperCountries_fractional <- calculate_country_citations(df, country_field, citation_col, "fractional")
    
    # Display the top 20 countries by citations (full counting)
    cat("\n=== TOP 20 COUNTRIES BY TOTAL CITATIONS (ALL AUTHORS, FULL COUNTING) ===\n")
    print(head(TCperCountries_full, 20))
    
    # Save the results to CSV files
    write.csv(TCperCountries_full, "citations_per_country_full.csv", row.names = FALSE)
    write.csv(TCperCountries_fractional, "citations_per_country_fractional.csv", row.names = FALSE)
    
    # Create visualizations for the top 10 countries
    if(nrow(TCperCountries_full) > 0) {
      top_n <- min(10, nrow(TCperCountries_full))
      top_countries <- head(TCperCountries_full, top_n)
      
      citations_plot <- ggplot(top_countries, aes(x = reorder(Country, Citations), y = Citations)) +
        geom_bar(stat = "identity", fill = "purple") +
        coord_flip() +
        theme_minimal() +
        labs(title = paste("Top", top_n, "Countries by Total Citations (All Authors)"),
             x = "Country",
             y = "Number of Citations")
      
      print(citations_plot)
      ggsave("top_countries_by_citations_all.png", citations_plot, width = 10, height = 6, dpi = 300)
    }
    
  }, error = function(e) {
    cat("Error in calculating citations per country (all authors):", e$message, "\n")
  })
}

# Calculate citations for corresponding author countries
if(!is.null(corresponding_country_field) && !is.null(citation_col)) {
  tryCatch({
    # Calculate using full counting for corresponding authors
    TCperCountries_corresponding <- calculate_country_citations(df, corresponding_country_field, citation_col, "full")
    
    # Display the top 20 countries by citations (corresponding authors)
    cat("\n=== TOP 20 COUNTRIES BY TOTAL CITATIONS (CORRESPONDING AUTHORS ONLY) ===\n")
    print(head(TCperCountries_corresponding, 20))
    
    # Save the results to a CSV file
    write.csv(TCperCountries_corresponding, "citations_per_country_corresponding.csv", row.names = FALSE)
    
    # Create a visualization for the top 10 countries
    if(nrow(TCperCountries_corresponding) > 0) {
      top_n <- min(10, nrow(TCperCountries_corresponding))
      top_countries <- head(TCperCountries_corresponding, top_n)
      
      corr_citations_plot <- ggplot(top_countries, aes(x = reorder(Country, Citations), y = Citations)) +
        geom_bar(stat = "identity", fill = "lightblue") +
        coord_flip() +
        theme_minimal() +
        labs(title = paste("Top", top_n, "Countries by Citations (Corresponding Authors)"),
             x = "Country",
             y = "Number of Citations")
      
      print(corr_citations_plot)
      ggsave("top_countries_by_citations_corresponding.png", corr_citations_plot, width = 10, height = 6, dpi = 300)
    }
    
  }, error = function(e) {
    cat("Error in calculating citations per country (corresponding authors):", e$message, "\n")
  })
} else {
  cat("Corresponding author country column not found. Skipping corresponding author analysis.\n")
}

# If neither analysis was possible
if(is.null(country_field) && is.null(corresponding_country_field)) {
  cat("Could not calculate citations per country. Missing country columns.\n")
}

# Print summary of the bibliometric analysis
cat("\n=== SUMMARY OF BIBLIOMETRIC ANALYSIS ===\n")
print(summary_results)
# Load required libraries
library(bibliometrix)
library(dplyr)
library(ggplot2)

# Set working directory if needed
# setwd("your/path/here")

# 1. Import and preprocess data
# Make sure your Scopus export file is in the working directory
file_path <- "Scopus_VR_ED_full_filters.csv"

# Try to import the data with error handling
tryCatch({
  df <- convert2df(file_path, dbsource = "scopus", format = "csv")
  
  # Print summary information about the dataset
  cat("\nDataset successfully loaded!\n")
  cat("Number of documents:", nrow(df), "\n")
  cat("Number of columns:", ncol(df), "\n\n")
  
}, error = function(e) {
  cat("Error importing data:", e$message, "\n")
  cat("Trying alternative import method...\n")
  
  # If convert2df fails, try reading directly with read.csv
  df <- read.csv(file_path, stringsAsFactors = FALSE, check.names = FALSE)
  cat("Data imported using read.csv instead. Some bibliometrix functions may be limited.\n")
})

# First filter out publications from 2025
year_column <- NULL
if("PY" %in% names(df)) {
  year_column <- "PY"
} else if("Year" %in% names(df)) {
  year_column <- "Year"
} else {
  # Look for any column that might contain year information
  year_cols <- grep("year|date|PY", names(df), ignore.case = TRUE)
  if(length(year_cols) > 0) {
    year_column <- names(df)[year_cols[1]]
  }
}

if(!is.null(year_column)) {
  # Convert year to numeric and filter out 2025
  df[[year_column]] <- as.numeric(as.character(df[[year_column]]))
  df_filtered <- df[df[[year_column]] != 2025, ]
  cat("Excluded publications from 2025. Dataset now has", nrow(df_filtered), "documents.\n")
  
  # Replace df with the filtered version
  df <- df_filtered
} else {
  cat("No year column found. Could not filter by year.\n")
}

# Create a bibliometric object
results <- biblioAnalysis(df)
summary_results <- summary(results)

# 2. Analyze top affiliations
# Extract and analyze affiliations - handle different column naming conventions
# First, check what columns are available
print("Available columns in the dataset:")
print(names(df))

# Check if affiliation columns exist and use them accordingly
if("AU_UN" %in% names(df)) {
  # If AU_UN exists, use it directly
  affiliations <- df$AU_UN
} else if("AU1_CO" %in% names(df)) {
  # Some Scopus exports use AU1_CO, AU1_UN format
  affiliations <- df$AU1_UN
} else if("Affiliations" %in% names(df)) {
  # Sometimes affiliations are under this name
  affiliations <- df$Affiliations
} else {
  # If none of the expected columns exist, try to find a column with "affiliation" in its name
  affiliation_cols <- grep("affil|univ|instit", names(df), ignore.case = TRUE)
  if(length(affiliation_cols) > 0) {
    affiliations <- df[[affiliation_cols[1]]]
  } else {
    # If no affiliation column found
    cat("No affiliation column found in the dataset. Column names are:", names(df), "\n")
    affiliations <- character(0)
  }
}

# Process affiliations if they exist
if(length(affiliations) > 0) {
  # Split and count affiliations
  all_affiliations <- unlist(strsplit(as.character(affiliations), ";"))
  all_affiliations <- trimws(all_affiliations)
  all_affiliations <- all_affiliations[all_affiliations != ""]
  affiliation_counts <- table(all_affiliations)
  top_affiliations <- sort(affiliation_counts, decreasing = TRUE)[1:min(20, length(affiliation_counts))]
} else {
  top_affiliations <- character(0)
}

# Create a data frame for plotting
if(length(top_affiliations) > 0) {
  top_aff_df <- data.frame(
    Affiliation = names(top_affiliations),
    Publications = as.numeric(top_affiliations)
  )
} else {
  top_aff_df <- data.frame(Affiliation = character(0), Publications = numeric(0))
}

# 3. Analyze top journals
# Extract and count journals
journals <- df %>%
  select(SO) %>%
  filter(!is.na(SO))

journal_counts <- table(journals$SO)
top_journals <- sort(journal_counts, decreasing = TRUE)[1:min(20, length(journal_counts))]

# Create a data frame for plotting
top_journal_df <- data.frame(
  Journal = names(top_journals),
  Publications = as.numeric(top_journals)
)

# 4. Define function to calculate h-index for journals
calculate_journal_h_index <- function(df) {
  # Get list of unique journals
  journals <- unique(df$SO)
  journal_h_index <- data.frame(Journal = character(), H_Index = numeric(), stringsAsFactors = FALSE)
  
  # Check if citation column exists
  citation_col <- NULL
  if("TC" %in% names(df)) {
    citation_col <- "TC"
  } else if("Citations" %in% names(df)) {
    citation_col <- "Citations"
  } else {
    # Look for any column containing citation information
    citation_cols <- grep("cit", names(df), ignore.case = TRUE)
    if(length(citation_cols) > 0) {
      citation_col <- names(df)[citation_cols[1]]
    }
  }
  
  # If citation column exists
  if(!is.null(citation_col)) {
    # For each journal
    for (journal in journals) {
      # Get all articles from this journal
      journal_articles <- df[df$SO == journal, ]
      
      # Get citation counts for these articles
      citations <- suppressWarnings(as.numeric(journal_articles[[citation_col]]))
      citations <- citations[!is.na(citations)]
      
      if(length(citations) > 0) {
        # Calculate h-index
        sorted_citations <- sort(citations, decreasing = TRUE)
        h_index <- sum(sorted_citations >= seq_along(sorted_citations))
      } else {
        h_index <- 0
      }
      
      # Add to dataframe
      journal_h_index <- rbind(journal_h_index, data.frame(Journal = journal, H_Index = h_index))
    }
    
    # Sort by h-index
    journal_h_index <- journal_h_index[order(journal_h_index$H_Index, decreasing = TRUE), ]
  } else {
    cat("No citation column found in the dataset. Cannot calculate h-index.\n")
  }
  
  return(journal_h_index)
}

# 5. Define function to create journal h-index table
create_journal_h_table <- function(journal_h_index, top_n = 20) {
  # Merge with publication counts if available
  if(exists("top_journal_df")) {
    merged_table <- merge(journal_h_index, top_journal_df, by.x = "Journal", by.y = "Journal", all.x = TRUE)
    names(merged_table)[names(merged_table) == "Publications"] <- "Num_Publications"
    merged_table$Num_Publications[is.na(merged_table$Num_Publications)] <- 0
  } else {
    # Count publications per journal manually
    journal_counts <- table(df$SO)
    merged_table <- cbind(journal_h_index, 
                         Num_Publications = as.vector(journal_counts[match(journal_h_index$Journal, names(journal_counts))]))
  }
  
  # Sort by H-Index
  merged_table <- merged_table[order(merged_table$H_Index, decreasing = TRUE), ]
  
  # Select top N journals
  top_table <- head(merged_table, top_n)
  
  # Print the table
  cat("\n=== TOP", top_n, "JOURNALS WITH H-INDEX AND PUBLICATION COUNT ===\n")
  print(top_table)
  
  # Save as CSV
  write.csv(merged_table, "journals_h_index_and_publications.csv", row.names = FALSE)
  
  return(top_table)
}

# 6. Calculate journal h-indices and create table
journal_h_index <- calculate_journal_h_index(df)
top_journals_h_index <- head(journal_h_index, 20)

# Create and display the combined journal h-index table
journal_h_table <- create_journal_h_table(journal_h_index)

# 7. Create visualizations
# Plot top affiliations
if(nrow(top_aff_df) > 0) {
  ggplot(top_aff_df[1:min(10, nrow(top_aff_df)),], aes(x = reorder(Affiliation, Publications), y = Publications)) +
    geom_bar(stat = "identity", fill = "skyblue") +
    coord_flip() +
    theme_minimal() +
    labs(title = "Top 10 Affiliations by Number of Publications",
         x = "Affiliation",
         y = "Number of Publications")
}

# Plot top journals
ggplot(top_journal_df[1:min(10, nrow(top_journal_df)),], aes(x = reorder(Journal, Publications), y = Publications)) +
  geom_bar(stat = "identity", fill = "lightgreen") +
  coord_flip() +
  theme_minimal() +
  labs(title = "Top 10 Journals by Number of Publications",
       x = "Journal",
       y = "Number of Publications")

# Plot h-index of top journals
ggplot(top_journals_h_index[1:min(10, nrow(top_journals_h_index)),], aes(x = reorder(Journal, H_Index), y = H_Index)) +
  geom_bar(stat = "identity", fill = "salmon") +
  coord_flip() +
  theme_minimal() +
  labs(title = "Top 10 Journals by H-Index",
       x = "Journal",
       y = "H-Index")

# Create a visualization of the journal h-index table
if(nrow(journal_h_table) > 0) {
  # Select top 15 for better visualization
  plot_data <- head(journal_h_table, 15)
  
  # Create a plot that shows both h-index and publication count
  h_index_plot <- ggplot(plot_data, aes(x = reorder(Journal, H_Index))) +
    geom_bar(aes(y = H_Index), stat = "identity", fill = "salmon", alpha = 0.7) +
    geom_text(aes(y = H_Index + 0.5, label = H_Index), size = 3) +
    geom_bar(aes(y = Num_Publications/max(Num_Publications) * max(H_Index) * 0.8), 
             stat = "identity", fill = "skyblue", alpha = 0.5) +
    scale_y_continuous(
      name = "H-Index",
      sec.axis = sec_axis(~./max(plot_data$H_Index) * max(plot_data$Num_Publications) * 1.25, 
                         name = "Number of Publications")
    ) +
    coord_flip() +
    theme_minimal() +
    labs(title = "Top Journals: H-Index (red) and Publication Count (blue)",
         x = "Journal") +
    theme(axis.text.y = element_text(size = 8))
  
  # Print the plot
  print(h_index_plot)
  
  # Save the plot
  ggsave("journal_h_index_and_publications.png", h_index_plot, width = 12, height = 8, dpi = 300)
}

# 8. Save results to files
write.csv(top_aff_df, "top_affiliations.csv", row.names = FALSE)
write.csv(top_journal_df, "top_journals.csv", row.names = FALSE)
write.csv(top_journals_h_index, "journal_h_index.csv", row.names = FALSE)

# 9. Additional bibliometric analyses
# Country collaboration - adjust for possible different column names
country_field <- NULL
if("AU_CO" %in% names(df)) {
  country_field <- "AU_CO"
} else if("Countries" %in% names(df)) {
  country_field <- "Countries"
} else {
  country_cols <- grep("countr", names(df), ignore.case = TRUE)
  if(length(country_cols) > 0) {
    country_field <- names(df)[country_cols[1]]
  }
}

if(!is.null(country_field)) {
  tryCatch({
    country_collab <- metaTagExtraction(df, Field = country_field, sep = ";")
    country_matrix <- biblioNetwork(country_collab, analysis = "collaboration", network = "countries")
    # You can visualize this with networkPlot if desired
  }, error = function(e) {
    cat("Error in country collaboration analysis:", e$message, "\n")
  })
} else {
  cat("No country column found for collaboration analysis.\n")
}

# Keyword co-occurrence - adjust for possible different column names
keyword_field <- NULL
if("DE" %in% names(df)) {
  keyword_field <- "DE"
} else if("ID" %in% names(df)) {
  keyword_field <- "ID"
} else if("Keywords" %in% names(df)) {
  keyword_field <- "Keywords"
} else {
  keyword_cols <- grep("keyword", names(df), ignore.case = TRUE)
  if(length(keyword_cols) > 0) {
    keyword_field <- names(df)[keyword_cols[1]]
  }
}

if(!is.null(keyword_field)) {
  tryCatch({
    keyword_co <- metaTagExtraction(df, Field = keyword_field, sep = ";")
    keyword_matrix <- biblioNetwork(keyword_co, analysis = "co-occurrences", network = "keywords")
  }, error = function(e) {
    cat("Error in keyword co-occurrence analysis:", e$message, "\n")
  })
} else {
  cat("No keyword column found for co-occurrence analysis.\n")
}

# 10. Analyze Total Citations per Country (with options for counting method)
cat("\n=== ANALYZING TOTAL CITATIONS PER COUNTRY ===\n")

# Find country columns - look for both general and corresponding author countries
country_field <- NULL
corresponding_country_field <- NULL

# Check for regular country field
if("AU_CO" %in% names(df)) {
  country_field <- "AU_CO"
} else if("Countries" %in% names(df)) {
  country_field <- "Countries"
} else {
  country_cols <- grep("countr", names(df), ignore.case = TRUE)
  if(length(country_cols) > 0) {
    country_field <- names(df)[country_cols[1]]
  }
}

# Check for corresponding author country field
if("CO_CO" %in% names(df)) {
  corresponding_country_field <- "CO_CO"
} else if("RP_CO" %in% names(df)) {
  corresponding_country_field <- "RP_CO"
} else {
  corresponding_cols <- grep("correspond.*countr|RP.*CO", names(df), ignore.case = TRUE)
  if(length(corresponding_cols) > 0) {
    corresponding_country_field <- names(df)[corresponding_cols[1]]
  }
}

# Find citation column
citation_col <- NULL
if("TC" %in% names(df)) {
  citation_col <- "TC"
} else if("Citations" %in% names(df)) {
  citation_col <- "Citations"
} else {
  citation_cols <- grep("cit", names(df), ignore.case = TRUE)
  if(length(citation_cols) > 0) {
    citation_col <- names(df)[citation_cols[1]]
  }
}

# Function to calculate citations per country based on specified counting method
calculate_country_citations <- function(df, country_col, citation_col, method="full") {
  # Ensure we have the necessary columns
  if(is.null(country_col) || is.null(citation_col)) {
    return(NULL)
  }
  
  # Extract countries and ensure they're in a usable format
  countries <- df[[country_col]]
  countries <- as.character(countries)
  
  # Extract citations and ensure they're numeric
  citations <- suppressWarnings(as.numeric(df[[citation_col]]))
  citations[is.na(citations)] <- 0
  
  # Create a dataframe with countries and citations
  country_citations <- data.frame(Country = countries, Citations = citations)
  
  # Initialize vectors for results
  all_countries <- c()
  all_citations <- c()
  
  if(method == "full") {
    # Full counting: each country gets full credit for the paper's citations
    for(i in 1:nrow(country_citations)) {
      if(!is.na(country_citations$Country[i])) {
        countries_list <- unlist(strsplit(country_citations$Country[i], ";"))
        countries_list <- trimws(countries_list)
        
        # For each country in the list, add the citation count
        for(country in countries_list) {
          if(country != "") {
            all_countries <- c(all_countries, country)
            all_citations <- c(all_citations, country_citations$Citations[i])
          }
        }
      }
    }
  } else if(method == "fractional") {
    # Fractional counting: citations are divided among countries
    for(i in 1:nrow(country_citations)) {
      if(!is.na(country_citations$Country[i])) {
        countries_list <- unlist(strsplit(country_citations$Country[i], ";"))
        countries_list <- trimws(countries_list)
        countries_list <- countries_list[countries_list != ""]
        
        # Skip if no valid countries
        if(length(countries_list) == 0) next
        
        # Divide citations among countries
        fraction <- country_citations$Citations[i] / length(countries_list)
        
        # For each country in the list, add the fractional citation count
        for(country in countries_list) {
          all_countries <- c(all_countries, country)
          all_citations <- c(all_citations, fraction)
        }
      }
    }
  }
  
  # Create a new dataframe with the expanded data
  expanded_data <- data.frame(Country = all_countries, Citations = all_citations)
  
  # Sum citations by country
  TCperCountries <- aggregate(Citations ~ Country, data = expanded_data, sum)
  
  # Sort by citations in descending order
  TCperCountries <- TCperCountries[order(TCperCountries$Citations, decreasing = TRUE), ]
  
  return(TCperCountries)
}

# Calculate citations for all countries (full counting method)
if(!is.null(country_field) && !is.null(citation_col)) {
  tryCatch({
    # Calculate using full counting (every country gets full credit)
    TCperCountries_full <- calculate_country_citations(df, country_field, citation_col, "full")
    
    # Calculate using fractional counting (citations divided among countries)
    TCperCountries_fractional <- calculate_country_citations(df, country_field, citation_col, "fractional")
    
    # Display the top 20 countries by citations (full counting)
    cat("\n=== TOP 20 COUNTRIES BY TOTAL CITATIONS (ALL AUTHORS, FULL COUNTING) ===\n")
    print(head(TCperCountries_full, 20))
    
    # Save the results to CSV files
    write.csv(TCperCountries_full, "citations_per_country_full.csv", row.names = FALSE)
    write.csv(TCperCountries_fractional, "citations_per_country_fractional.csv", row.names = FALSE)
    
    # Create visualizations for the top 10 countries
    if(nrow(TCperCountries_full) > 0) {
      top_n <- min(10, nrow(TCperCountries_full))
      top_countries <- head(TCperCountries_full, top_n)
      
      citations_plot <- ggplot(top_countries, aes(x = reorder(Country, Citations), y = Citations)) +
        geom_bar(stat = "identity", fill = "purple") +
        coord_flip() +
        theme_minimal() +
        labs(title = paste("Top", top_n, "Countries by Total Citations (All Authors)"),
             x = "Country",
             y = "Number of Citations")
      
      print(citations_plot)
      ggsave("top_countries_by_citations_all.png", citations_plot, width = 10, height = 6, dpi = 300)
    }
    
  }, error = function(e) {
    cat("Error in calculating citations per country (all authors):", e$message, "\n")
  })
}

# Calculate citations for corresponding author countries
if(!is.null(corresponding_country_field) && !is.null(citation_col)) {
  tryCatch({
    # Calculate using full counting for corresponding authors
    TCperCountries_corresponding <- calculate_country_citations(df, corresponding_country_field, citation_col, "full")
    
    # Display the top 20 countries by citations (corresponding authors)
    cat("\n=== TOP 20 COUNTRIES BY TOTAL CITATIONS (CORRESPONDING AUTHORS ONLY) ===\n")
    print(head(TCperCountries_corresponding, 20))
    
    # Save the results to a CSV file
    write.csv(TCperCountries_corresponding, "citations_per_country_corresponding.csv", row.names = FALSE)
    
    # Create a visualization for the top 10 countries
    if(nrow(TCperCountries_corresponding) > 0) {
      top_n <- min(10, nrow(TCperCountries_corresponding))
      top_countries <- head(TCperCountries_corresponding, top_n)
      
      corr_citations_plot <- ggplot(top_countries, aes(x = reorder(Country, Citations), y = Citations)) +
        geom_bar(stat = "identity", fill = "lightblue") +
        coord_flip() +
        theme_minimal() +
        labs(title = paste("Top", top_n, "Countries by Citations (Corresponding Authors)"),
             x = "Country",
             y = "Number of Citations")
      
      print(corr_citations_plot)
      ggsave("top_countries_by_citations_corresponding.png", corr_citations_plot, width = 10, height = 6, dpi = 300)
    }
    
  }, error = function(e) {
    cat("Error in calculating citations per country (corresponding authors):", e$message, "\n")
  })
} else {
  cat("Corresponding author country column not found. Skipping corresponding author analysis.\n")
}

# If neither analysis was possible
if(is.null(country_field) && is.null(corresponding_country_field)) {
  cat("Could not calculate citations per country. Missing country columns.\n")
}



