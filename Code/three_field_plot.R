# Install bibliometrix if not already installed
install.packages("bibliometrix")

# Load the package
library(bibliometrix)

# Load your data (replace with your file)
M <- convert2df("your_file.bib", dbsource = "scopus", format = "bibtex")

# Do a bibliometric analysis
results <- biblioAnalysis(M, sep = ";")

# Improved Three-Field Plot
threeFieldsPlot(results,
                fields = c("AU_CO", "DE", "AU_UN"),  # Country, Keywords, University
                k = 10,                               # Top 10 items per field
                fontsize = 14,                        # Larger font size
                lab.cex = 1.5,                        # Label size
                lab.link.angle = 0,                   # Horizontal label orientation
                col = c("darkred", "orange", "steelblue"))  # Custom colors
