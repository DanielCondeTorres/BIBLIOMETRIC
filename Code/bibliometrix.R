# Instalar paquetes si es necesario
# install.packages("bibliometrix")
# install.packages("tidyverse")
# install.packages("igraph")

# Cargar librerías
library(bibliometrix)
library(tidyverse)
library(igraph)

# 1. Cargar y preparar datos ----------------------------------------------
file_path <- 'Scopus_VR_ED_full_filters.csv'

# Cargar datos y extraer metatags importantes
df <- convert2df(file_path, dbsource = "scopus", format = "csv") %>% filter(PY != 2025) %>%  metaTagExtraction(Field = "AU_CO") %>%  metaTagExtraction(Field = "CR")  # Para análisis de referencias

# Convertir columnas clave a numérico
df$PY <- as.numeric(df$PY)
df$TC <- as.numeric(df$TC)

# 2. Análisis básico de desempeño -----------------------------------------
results <- biblioAnalysis(df)
summary_results <- summary(results, k = 10, pause = FALSE)

# 3. Cálculo de métricas principales --------------------------------------
# Publicaciones
TP <- nrow(df)
NCA <- length(unique(unlist(strsplit(df$AU, ";")))) 
SA <- sum(str_count(df$AU, ";") == 0)
CA <- TP - SA
NAY <- length(unique(na.omit(df$PY)))
PAY <- round(TP/NAY, 2)

# Citas
TC <- sum(df$TC, na.rm = TRUE)
AC <- round(TC/TP, 2)

# Métricas combinadas
CI <- results$Collaboration$CI
CC <- results$Collaboration$CC
NCP <- sum(df$TC > 0, na.rm = TRUE)
PCP <- round(NCP/TP * 100, 2)
CCP <- ifelse(NCP > 0, round(TC/NCP, 2), 0)

# Índices
h_index <- Hindex(df, field = "author", sep = ";")$H
g_index <- Hindex(df, field = "author", sep = ";")$g
i10 <- sum(df$TC >= 10, na.rm = TRUE)
























# Función para guardar gráficos de redes
guardar_grafico <- function(expr, nombre_archivo, ancho = 10, alto = 8) {
  # Abrir dispositivo gráfico PDF
  pdf(paste0(nombre_archivo, ".pdf"), width = ancho, height = alto)
  
  # Ejecutar la expresión que genera el gráfico
  result <- tryCatch({
    expr
    TRUE
  }, error = function(e) {
    message("Error al generar el gráfico: ", e$message)
    FALSE
  })
  
  # Cerrar dispositivo gráfico
  dev.off()
  
  # También guardar como PNG para fácil visualización
  png(paste0(nombre_archivo, ".png"), width = ancho*100, height = alto*100, res = 100)
  tryCatch({
    expr
  }, error = function(e) {
    message("Error al generar versión PNG: ", e$message)
  })
  dev.off()
  
  # Informar resultado
  if(result) {
    cat("Gráfico guardado como", paste0(nombre_archivo, ".pdf"), "y", paste0(nombre_archivo, ".png"), "\n")
  } else {
    cat("No se pudo guardar el gráfico", nombre_archivo, "\n")
  }
  
  return(result)
}

# Nueva función para exportar redes como edge list
exportar_edge_list <- function(matriz_red, nombre_archivo) {
  # Convertir la matriz a un grafo igraph
  red_igraph <- graph_from_adjacency_matrix(matriz_red, mode = "undirected", weighted = TRUE)
  
  # Obtener la lista de aristas con pesos
  aristas <- as_data_frame(red_igraph, what = "edges")
  
  # Guardar solo en formato TXT
  write.table(aristas, paste0(nombre_archivo, "_edgelist.txt"), 
              sep = "\t", row.names = FALSE, quote = FALSE)
  
  cat("Red exportada como edge list en:", paste0(nombre_archivo, "_edgelist.txt"), "\n")
  
  return(aristas)
}

# 4. Mapeo científico con guardado de gráficos ---------------------------
cat("\n=== MAPEO CIENTÍFICO Y GUARDADO DE GRÁFICOS ===\n")

# Directorio de salida
dir_salida <- "resultados_bibliometricos"
# Crear directorio si no existe
if(!dir.exists(dir_salida)) {
  dir.create(dir_salida)
  cat("Directorio creado:", dir_salida, "\n")
}

# Ruta completa para archivos
ruta_completa <- function(nombre) {
  file.path(dir_salida, nombre)
}

# Análisis de co-citación (referencias)
cat("Ejecutando análisis de co-citación...\n")
NetMatrix <- biblioNetwork(df, analysis = "co-citation", network = "references")
# Exportar como edge list
exportar_edge_list(NetMatrix, ruta_completa("01_red_cocitacion_referencias"))
# Visualizar y guardar gráfico
guardar_grafico(
  networkPlot(NetMatrix, 
          #   n = 20,
             type = "fruchterman",
             labelsize = 0.7,
  ),
  ruta_completa("01_red_cocitacion_referencias")
)

# Acoplamiento bibliográfico (autores) - CORREGIDO: eliminado repel=TRUE
cat("Ejecutando análisis de acoplamiento bibliográfico...\n")
NetMatrix <- biblioNetwork(df, analysis = "coupling", network = "authors", sep = ";")
# Exportar como edge list
exportar_edge_list(NetMatrix, ruta_completa("02_red_acoplamiento_autores"))
# Visualizar y guardar gráfico
guardar_grafico(
  networkPlot(NetMatrix, 
           #   n = 20,
             type = "auto",
             ),
  ruta_completa("02_red_acoplamiento_autores")
)

# Análisis de co-palabras (keywords)
cat("Ejecutando análisis de co-palabras...\n")
tryCatch({
  # Ajustado para manejar el problema de superposición
  CS <- conceptualStructure(df, 
                         field = "ID", 
                         minDegree = 5, 
                         k.max = 5,
                         labelsize = 6)
  # Esta función guarda automáticamente sus resultados, no necesitamos guardarla explícitamente
  cat("Análisis conceptual guardado automáticamente por la función\n")
}, error = function(e) {
  cat("Error en análisis conceptual:", e$message, "\n")
})

# Análisis de co-autoría (países)
if("AU_CO" %in% colnames(df)){
  cat("Ejecutando análisis de co-autoría por países...\n")
  NetMatrix <- biblioNetwork(df, analysis = "collaboration", network = "countries")
  # Exportar como edge list
  exportar_edge_list(NetMatrix, ruta_completa("03_red_colaboracion_paises"))
  # Visualizar y guardar gráfico
  guardar_grafico(
    networkPlot(NetMatrix,
              halo = TRUE,
              labelsize = 0.8,
              edgesize = 0.8,
              alpha = 0.5,
              remove.multiple = TRUE,
              ),
    ruta_completa("03_red_colaboracion_paises")
  )
}

# Co-autoría (autores) - MODIFICADO: solo mostrar las etiquetas de los 10 más importantes
cat("Ejecutando análisis de co-autoría entre autores...\n")
NetMatrix <- biblioNetwork(df, analysis = "collaboration", network = "authors")
# Exportar como edge list
exportar_edge_list(NetMatrix, ruta_completa("04_red_colaboracion_autores"))

# Crear una versión modificada de networkPlot para mostrar solo los 10 más importantes
guardar_grafico({
  # Obtener métricas de centralidad para determinar los 10 nodos más importantes
  net_igraph <- graph_from_adjacency_matrix(NetMatrix, mode = "undirected")
  centralidad <- degree(net_igraph)
  nombres_nodos <- V(net_igraph)$name
  
  # Identificar los 10 nodos más importantes por grado de centralidad
  top10_indices <- order(centralidad, decreasing = TRUE)[1:min(10, length(centralidad))]
  top10_nombres <- nombres_nodos[top10_indices]
  
  # Crear vector de etiquetas donde solo los top 10 tendrán etiquetas y el resto serán vacías
  etiquetas_personalizadas <- rep("", length(nombres_nodos))
  for (i in 1:length(nombres_nodos)) {
    if (nombres_nodos[i] %in% top10_nombres) {
      etiquetas_personalizadas[i] <- nombres_nodos[i]
    }
  }
  
  # Realizar la visualización con etiquetas filtradas
  networkPlot(NetMatrix,
              type = "auto",
              label = etiquetas_personalizadas,  # Usar etiquetas personalizadas
              labelsize = 0.8,                   # Aumentado para mejor visibilidad
              )
},
  ruta_completa("04_red_colaboracion_autores")
)

# 5. Análisis de redes avanzado -------------------------------------------
# Crear objeto de red
cat("Creando red para análisis avanzado...\n")
net <- biblioNetwork(df, analysis = "collaboration", network = "authors")
# Exportar esta red principal como edge list
exportar_edge_list(net, ruta_completa("05_red_principal"))

# Convertir a grafo no dirigido para poder aplicar Louvain
network <- graph_from_adjacency_matrix(net, mode = "undirected")

# MODIFICADO: Visualización de red principal con solo top 10 etiquetas
guardar_grafico({
  # Calcular la centralidad
  centralidad <- degree(network)
  # Obtener los 10 nodos más importantes
  top10_indices <- order(centralidad, decreasing = TRUE)[1:min(10, length(centralidad))]
  
  # Crear vector de etiquetas donde solo los top 10 tendrán nombres
  vertex_labels <- rep(NA, length(V(network)))
  vertex_labels[top10_indices] <- V(network)$name[top10_indices]
  
  # Personalizar tamaños de nodos - más grandes para los importantes
  vertex_sizes <- rep(3, length(V(network)))
  vertex_sizes[top10_indices] <- 6
  
  # Personalizar colores - más destacados para los importantes
  vertex_colors <- rep("lightblue", length(V(network)))
  vertex_colors[top10_indices] <- "orangered"
  
  # Realizar la visualización con etiquetas filtradas - sin título
  plot(network,
       vertex.size = vertex_sizes,
       vertex.color = vertex_colors,
       vertex.label = vertex_labels,
       vertex.label.cex = 0.8,
       edge.arrow.size = 0.1,
       main = NULL)
},
  ruta_completa("05_red_principal")
)

# Métricas de centralidad
metrics <- data.frame(
  Autor = V(network)$name,
  Grado = degree(network),
  Intermediacion = round(betweenness(network), 2),
  Vector_Propio = round(eigen_centrality(network)$vector, 3)
)

# Clustering - con manejo de errores
clusters <- tryCatch({
  cat("Aplicando algoritmo de clustering Louvain...\n")
  cluster_louvain(network)
}, error = function(e) {
  cat("No se pudo realizar el clustering Louvain:", e$message, "\n")
  cat("Usando clustering por componentes como alternativa...\n")
  components(network)
})

metrics$Cluster <- membership(clusters)

# MODIFICADO: Visualizar comunidades con solo etiquetas para los top 10, sin título
guardar_grafico({
  # Obtener los 10 autores principales por centralidad
  centralidad <- degree(network)
  top10_indices <- order(centralidad, decreasing = TRUE)[1:min(10, length(centralidad))]
  
  # Crear vector de etiquetas donde solo los top 10 tendrán nombres
  vertex_labels <- rep(NA, length(V(network)))
  vertex_labels[top10_indices] <- V(network)$name[top10_indices]
  
  # Personalizar tamaños de nodos - más grandes para los importantes
  vertex_sizes <- rep(3, length(V(network)))
  vertex_sizes[top10_indices] <- 6
  
  # Realizar la visualización de comunidades con etiquetas filtradas, sin título
  plot(clusters, network,
       vertex.size = vertex_sizes,
       vertex.label = vertex_labels,
       vertex.label.cex = 0.8,
       main = NULL)
},
  ruta_completa("06_comunidades_red")
)

# Exportar métricas de red
write.csv(metrics, file.path(dir_salida, "metricas_redes.csv"), row.names = FALSE)
cat("Métricas de red exportadas a", file.path(dir_salida, "metricas_redes.csv"), "\n")

# Exportar clusters como atributo de nodos
nodos_clusters <- data.frame(
  Nodo = V(network)$name,
  Cluster = membership(clusters)
)
write.table(nodos_clusters, file.path(dir_salida, "nodos_clusters.txt"), 
            sep = "\t", row.names = FALSE, quote = FALSE)
cat("Información de clusters exportada a", file.path(dir_salida, "nodos_clusters.txt"), "\n")

# 6. Análisis temáticos adicionales ---------------------------------------
# Mapa de co-ocurrencias de palabras clave
cat("Creando mapa de co-ocurrencias de palabras clave...\n")
tryCatch({
  if("DE" %in% colnames(df) || "ID" %in% colnames(df)) {
    # Usar Keywords Plus (ID) o Keywords (DE)
    campo_keywords <- ifelse("ID" %in% colnames(df), "ID", "DE")
    
    NetMatrix <- biblioNetwork(df, analysis = "co-occurrences", network = campo_keywords, sep = ";")
    # Exportar como edge list
    exportar_edge_list(NetMatrix, ruta_completa("07_red_coocurrencias_keywords"))
    # Visualizar y guardar gráfico
    guardar_grafico(
      networkPlot(NetMatrix,
                n = 30,
                type = "kamada",
                labelsize = 0.7,
                ),
      ruta_completa("07_red_coocurrencias_keywords")
    )
  } else {
    cat("No se encontraron columnas de palabras clave (DE o ID) para el análisis\n")
  }
}, error = function(e) {
  cat("Error en mapa de co-ocurrencias:", e$message, "\n")
})

# Mapa de temas usando análisis de correspondencia
cat("Creando mapa temático...\n")
tryCatch({
  if("ID" %in% colnames(df)) {
    # Modificado para reducir el número de elementos y evitar superposiciones
    thematicMap <- thematicMap(df, field = "ID", n = 200, minfreq = 8,
                           stemming = FALSE, size = 0.5, n.labels = 5)
    cat("Mapa temático generado\n")
  } else {
    cat("No se encontró columna ID para análisis temático\n")
  }
}, error = function(e) {
  cat("Error en mapa temático:", e$message, "\n")
})

# 7. Evolución temporal --------------------------------------------------
# Análisis de tendencias de temas
cat("Analizando evolución temporal de temas...\n")
tryCatch({
  if("ID" %in% colnames(df)) {
    # Aumentado min.freq para reducir elementos y evitar saturación
    topicEvolution <- fieldByYear(df, field = "ID", timespan = NULL, 
                              min.freq = 8, n.items = 5, graph = TRUE)
    # Guardar tendencias
    guardar_grafico(
      plot(topicEvolution$graph),
      ruta_completa("08_evolucion_temas")
    )
  } else {
    cat("No se encontró columna ID para análisis de evolución\n")
  }
}, error = function(e) {
  cat("Error en análisis de evolución:", e$message, "\n")
})

# Análisis de autores por año
cat("Analizando contribución de autores por año...\n")
tryCatch({
  topAU <- authorProdOverTime(df, k = 10)
  # Esta función genera sus propios gráficos
  cat("Análisis de producción de autores generado\n")
}, error = function(e) {
  cat("Error en análisis de autores por año:", e$message, "\n")
})

cat("\nTodos los análisis de redes completados y guardados en el directorio:", dir_salida, "\n")
cat("Los edge lists se encuentran en archivos TXT en:", dir_salida, "\n")
cat("Por favor, revisa ese directorio para encontrar todos los archivos PDF, PNG y edge lists generados.\n")