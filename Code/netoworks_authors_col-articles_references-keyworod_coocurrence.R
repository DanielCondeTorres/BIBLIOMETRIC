# 1. Cargar librerías
library(bibliometrix)   # paquete para análisis bibliométrico :contentReference[oaicite:3]{index=3}
library(dplyr)
library(igraph)         # paquete para análisis de redes :contentReference[oaicite:4]{index=4}

# 2. Importar datos de Scopus
file_path <- "Scopus_VR_ED_full_filters.csv"
df <- convert2df(file_path, dbsource = "scopus", format = "csv")

# 3. Filtrar para excluir 2025
df <- df %>% filter(PY < 2025)

# 4. Extraer matriz de red (e.g., acoplamiento bibliográfico)
M <- biblioNetwork(df, analysis = "coupling", network = "references", sep = ";")

# 5. Crear objeto igraph desde la matriz (no dirigido, ponderado)
g <- graph_from_adjacency_matrix(M, mode = "undirected", weighted = TRUE)

# 6. Calcular medidas de centralidad
deg    <- degree(g, mode = "all")                     # grado :contentReference[oaicite:5]{index=5}
wdeg   <- strength(g, mode = "all")                   # grado ponderado :contentReference[oaicite:6]{index=6}
betw   <- betweenness(g, directed = FALSE)            # intermediación :contentReference[oaicite:7]{index=7}
eigen  <- eigen_centrality(g, directed = FALSE)$vector  # autocentralidad :contentReference[oaicite:8]{index=8}

# 7. Crear un data.frame de resultados
results <- data.frame(
  Article   = names(deg),
  Degree    = deg,
  WDegree   = wdeg,
  Betweenness = betw,
  Eigen     = eigen,
  row.names = NULL,
  stringsAsFactors = FALSE
)

# 8. Extraer los top 3 para cada medida
top_degree    <- slice_max(results, Degree,    n = 3)
top_wdegree   <- slice_max(results, WDegree,   n = 3)
top_betw      <- slice_max(results, Betweenness, n = 3)
top_eigen     <- slice_max(results, Eigen,     n = 3)

# 9. Combinar para tabla final
table4 <- bind_rows(
  mutate(top_degree, Measure = "Degree"),
  mutate(top_wdegree, Measure = "Weighted Degree"),
  mutate(top_betw,    Measure = "Betweenness"),
  mutate(top_eigen,   Measure = "Eigen-centrality")
) %>%
  select(Measure, Article, everything())

print(table4)



# 1. Cargar librerías
library(bibliometrix)
library(dplyr)
library(igraph)

# 2. Importar datos
file_path <- "Scopus_VR_ED_full_filters.csv"
df <- convert2df(file_path, dbsource = "scopus", format = "csv")

# 3. Filtrar para excluir 2025
df <- df %>% filter(PY < 2025)

# 4. Crear matriz de coautoría (análisis = "collaboration", unidad = "authors")
#    sep = ";" indica que los campos de autor están separados por punto y coma
A <- biblioNetwork(df, analysis = "collaboration", network = "authors", sep = ";")

# 5. Convertir la matriz en grafo ponderado no dirigido
gA <- graph_from_adjacency_matrix(A, mode = "undirected", weighted = TRUE)

# 6. Calcular medidas de centralidad para cada autor
degA   <- degree(gA, mode = "all")                     # grado
wdegA  <- strength(gA, mode = "all")                   # grado ponderado
betwA  <- betweenness(gA, directed = FALSE, normalized = TRUE)  # intermediación normalizada
eigenA <- eigen_centrality(gA, directed = FALSE)$vector # autocentralidad

# 7. Montar data.frame de resultados
auth_results <- tibble(
  Author        = names(degA),
  Degree        = degA,
  WDegree       = wdegA,
  Betweenness   = betwA,
  EigenCentrality = eigenA
)

# 8. Extraer top 3 para cada medida
top_deg_auth  <- slice_max(auth_results, Degree,    n = 3)
top_wdeg_auth <- slice_max(auth_results, WDegree,   n = 3)
top_betw_auth <- slice_max(auth_results, Betweenness, n = 3)
top_eig_auth  <- slice_max(auth_results, EigenCentrality, n = 3)

# 9. Combinar en tabla final
table_auth <- bind_rows(
  mutate(top_deg_auth,  Measure = "Degree"),
  mutate(top_wdeg_auth, Measure = "Weighted Degree"),
  mutate(top_betw_auth, Measure = "Betweenness"),
  mutate(top_eig_auth,  Measure = "Eigen-centrality")
) %>%
  select(Measure, Author, Degree, WDegree, Betweenness, EigenCentrality)

print(table_auth)






# 1. Cargar librerías
library(bibliometrix)
library(igraph)
library(dplyr)

# 2. Importar y filtrar datos
file_path <- "Scopus_VR_ED_full_filters.csv"
df <- convert2df(file_path, dbsource = "scopus", format = "csv")
df <- filter(df, PY < 2025)

# 3. Matriz de co-ocurrencias de keywords
NetMatrix <- biblioNetwork(df,
                           analysis = "co-occurrences",
                           network  = "keywords",
                           sep      = ";")

# 4. Contar frecuencia de cada keyword
kw_list <- strsplit(as.character(df$DE), split = ";")
kw_vec  <- trimws(unlist(kw_list))
kw_freq <- as.data.frame(table(kw_vec), stringsAsFactors = FALSE) %>%
  rename(Keyword = kw_vec, Occurrence = Freq)

# 5. Grafo ponderado
gk <- graph_from_adjacency_matrix(NetMatrix,
                                  mode     = "undirected",
                                  weighted = TRUE,
                                  diag     = FALSE)

# 6. Top n keywords por ocurrencia
top_kw_occ <- kw_freq %>%
  slice_max(Occurrence, n = 10) %>%        # aquí puedes cambiar n
  mutate(Measure = "Occurrence")

# 7. Extraer edgelist completa
edge_list <- as_data_frame(gk, what = "edges") %>%
  rename(Keyword1 = from,
         Keyword2 = to,
         Cooccurrence = weight)

# 8. Top n pares por co-ocurrencia
top_kw_cooc <- edge_list %>%
  slice_max(Cooccurrence, n = 10) %>%      # aquí también puedes cambiar n
  mutate(Measure = "Co-occurrence")

# 9. Combinar ambos rankings en una sola tabla
top_keywords <- bind_rows(
  top_kw_occ  %>% select(Keyword, Occurrence, Measure),
  top_kw_cooc %>% rename(Keyword = Keyword1, Occurrence = Cooccurrence) %>%
                  select(Keyword, Occurrence, Measure)
)

# 10. Mostrar resultados
print(top_keywords)

# 9. Exportar la edgelist completa a un .txt
write.table(
  edge_list,
  file      = "edgelist_co_ocurrence_keywords.txt",
  sep       = "\t",         # separador de tabulaciones
  row.names = FALSE,        # no incluir índices de fila
  quote     = FALSE         # no encerrar cadenas entre comillas
)





# 1. Cargar librerías
library(bibliometrix)   # para extraer matrices bibliométricas :contentReference[oaicite:3]{index=3}
library(igraph)         # para análisis y visualización de redes :contentReference[oaicite:4]{index=4}

# 2. Importar y filtrar datos
file_path <- "Scopus_VR_ED_full_filters.csv"
df <- convert2df(file_path, dbsource = "scopus", format = "csv")  # :contentReference[oaicite:5]{index=5}
df <- subset(df, PY < 2025)

# 3. Matriz de co-ocurrencias de keywords
NetMatrix <- biblioNetwork(df,
                           analysis = "co-occurrences",
                           network  = "keywords",
                           sep      = ";")          # :contentReference[oaicite:6]{index=6}

# 4. Contar frecuencia de cada keyword
#   - Extraemos todos los keywords en un vector
kw_list <- strsplit(df$DE, split = ";")                   
kw_vec  <- trimws(unlist(kw_list))                         # :contentReference[oaicite:7]{index=7}
kw_freq <- table(kw_vec)                                    # frecuencia de aparición :contentReference[oaicite:8]{index=8}

# 5. Crear grafo ponderado
gk <- graph_from_adjacency_matrix(NetMatrix,
                                  mode     = "undirected",
                                  weighted = TRUE,
                                  diag     = FALSE)     # :contentReference[oaicite:9]{index=9}

# 6. Asignar atributos de visualización
V(gk)$size      <- as.numeric(kw_freq[V(gk)$name])         # tamaño ~ ocurrencias  :contentReference[oaicite:10]{index=10}
E(gk)$width     <- E(gk)$weight                             # grosor ~ co-ocurrencias :contentReference[oaicite:11]{index=11}
V(gk)$label.cex <- 0.7                                      # tamaño de etiqueta

# 7. Dibujar la red
plot(gk,
     layout      = layout_with_fr,      # algoritmo Fruchterman-Reingold
     vertex.color= "steelblue",         # color genérico
     vertex.frame.color = NA,           # sin borde
     edge.color  = "gray70",            # color de enlaces
     main        = "Keyword Co-occurrence Network")
