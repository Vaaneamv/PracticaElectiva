from qgis.core import QgsProject
import numpy as np
import scipy.stats as stats

# Carga del proyecto de QGIS
project = QgsProject.instance()

# Acceder a las capas
nodes_layer = project.mapLayersByName('nodes')[0]
earthquake_layer = project.mapLayersByName('earthquake')[0]

# Extraer datos de las capas
nodos = [(feature.id(), feature.geometry().asPoint().x(), feature.geometry().asPoint().y()) for feature in nodes_layer.getFeatures()]
terremotos = [(feature.id(), feature.geometry().asPoint().x(), feature.geometry().asPoint().y(), feature['mag']) for feature in earthquake_layer.getFeatures()]

# Parámetros de la simulación
num_simulaciones = 1000
magnitudes = stats.norm(5, 0.5)  # Ajustar según sea necesario
distancia_max_impacto = 100  # Máxima distancia de impacto significativo

# Función para calcular la intensidad del impacto en un nodo
def calcular_intensidad(distancia, magnitud):
    if distancia > distancia_max_impacto:
        return 0
    return magnitud / distancia  # Simple modelo inverso

# Simulación de Monte Carlo
resultados = np.zeros((num_simulaciones, len(nodos)))

for i in range(num_simulaciones):
    # Simular magnitudes y ubicaciones de terremotos
    magnitudes_simuladas = magnitudes.rvs(size=len(terremotos))
    for j, nodo in enumerate(nodos):
        impacto_maximo = 0
        for terremoto, magnitud in zip(terremotos, magnitudes_simuladas):
            distancia = np.sqrt((terremoto[1] - nodo[1])**2 + (terremoto[2] - nodo[2])**2)
            impacto = calcular_intensidad(distancia, magnitud)
            if impacto > impacto_maximo:
                impacto_maximo = impacto
        resultados[i, j] = impacto_maximo

# Estadísticas de resultados
intensidades_promedio = np.mean(resultados, axis=0)
print("Intensidades promedio por nodo:", intensidades_promedio)
