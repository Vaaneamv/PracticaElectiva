import json
import numpy as np
import scipy.stats as stats
from qgis.core import QgsGeometry, QgsPointXY

# Cargar el archivo JSON con los datos de los tsunamis
with open('tsunami_polygons.json', 'r') as file:
    tsunami_data = json.load(file)

# Simulación de nodos cargados (estos deberían venir de tu capa de nodos)
nodes = [
    {'id': 1, 'coordinates': (20.5, 145.0)},
    {'id': 2, 'coordinates': (21.0, 145.5)},
    # Agrega más nodos según sea necesario
]

# Extraer datos de los tsunamis
terremotos = [
    {
        'id': idx,
        'epicenter': QgsPointXY(tsunami['epicenter'][0], tsunami['epicenter'][1]),
        'magnitude': tsunami['magnitude'],
        'polygon': QgsGeometry.fromPolygonXY([[QgsPointXY(coord[0], coord[1]) for coord in tsunami['polygon']]])
    }
    for idx, tsunami in enumerate(tsunami_data)
]

# Parámetros de la simulación
num_simulaciones = 1000
magnitudes = stats.norm(8, 1)  # Suponer magnitudes altas para tsunamis
distancia_max_impacto = 5000  # Máxima distancia de impacto significativo

# Función para calcular la intensidad del impacto en un nodo
def calcular_intensidad(distancia, magnitud):
    if distancia > distancia_max_impacto:
        return 0
    return magnitud * (1 - distancia / distancia_max_impacto)  # Modelo de disipación para tsunamis

# Simulación de Monte Carlo
resultados = np.zeros((num_simulaciones, len(nodes)))

for i in range(num_simulaciones):
    magnitudes_simuladas = magnitudes.rvs(size=len(terremotos))
    for j, nodo in enumerate(nodes):
        impacto_maximo = 0
        node_geom = QgsGeometry.fromPointXY(QgsPointXY(nodo['coordinates'][0], nodo['coordinates'][1]))
        for terremoto, magnitud in zip(terremotos, magnitudes_simuladas):
            distancia = node_geom.distance(terremoto['polygon'])
            impacto = calcular_intensidad(distancia, magnitud)
            if impacto > impacto_maximo:
                impacto_maximo = impacto
        resultados[i, j] = impacto_maximo

# Estadísticas de resultados
intensidades_promedio = np.mean(resultados, axis=0)
print("Intensidades promedio por nodo:", intensidades_promedio)
