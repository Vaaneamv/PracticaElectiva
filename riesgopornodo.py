from qgis.core import QgsProject
import numpy as np
import scipy.stats as stats

# Carga del proyecto de QGIS
project = QgsProject.instance()

# Acceder a la capa de nodos y terremotos
nodes_layer = project.mapLayersByName('nodes')[0]
earthquake_layer = project.mapLayersByName('earthquake')[0]

# Extraer datos de las capas
nodos = [(feature.id(), feature.geometry().asPoint().x(), feature.geometry().asPoint().y()) for feature in nodes_layer.getFeatures()]
terremotos = [(feature.id(), feature.geometry().asPoint().x(), feature.geometry().asPoint().y(), feature['mag']) for feature in earthquake_layer.getFeatures() if feature['mag'] > 6.5]  # Solo terremotos fuertes pueden generar tsunamis

# Parámetros de la simulación
num_simulaciones = 1000
distancia_max_impacto = 5000  # Máxima distancia de impacto significativo para tsunamis

# Simulación de Monte Carlo para predecir la generación de tsunamis
resultados = np.zeros((num_simulaciones, len(nodos)))

for i in range(num_simulaciones):
    for j, nodo in enumerate(nodos):
        riesgo_tsunami = 0
        for terremoto in terremotos:
            distancia = np.sqrt((terremoto[1] - nodo[1])**2 + (terremoto[2] - nodo[2])**2)
            if distancia < distancia_max_impacto:
                # Considerar otros factores como la magnitud del terremoto
                riesgo_tsunami += terremoto[3] / distancia  # Ajustar por magnitud y distancia
        resultados[i, j] = riesgo_tsunami

# Estadísticas de resultados
tsunami_riesgo_promedio = np.mean(resultados, axis=0)
print("Riesgo promedio de tsunami por nodo:", tsunami_riesgo_promedio)
