from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsField,
    QgsFillSymbol,
    QgsRendererRange,
    QgsGraduatedSymbolRenderer,
    QgsPointXY,
)
from PyQt5.QtGui import QColor
import math

# Obtener la capa de terremotos
earthquake_layer_name = "earthquake"
earthquake_layers = QgsProject.instance().mapLayersByName(earthquake_layer_name)

if not earthquake_layers:
    raise Exception("Capa de terremotos no encontrada.")

earthquake_layer = earthquake_layers[0]

# Crear una capa para los polígonos
polygon_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "Polígonos de Terremotos", "memory")
provider_polygon = polygon_layer.dataProvider()
provider_polygon.addAttributes([QgsField("Magnitud", 10)])
polygon_layer.updateFields()

# Definir el radio para el buffer (50 km)
buffer_radius_km = 50  # Radio en kilómetros
buffer_radius_degrees = buffer_radius_km / 111.32  # Aproximación a grados para WGS84
segments = 36  # Para suavizar el polígono

# Crear polígonos alrededor de puntos de terremotos
polygons = []

for feature in earthquake_layer.getFeatures():
    point_geometry = feature.geometry()  # Obtener la geometría del terremoto
    magnitude = feature["mag"]  # Magnitud del terremoto
    
    # Crear un buffer para el polígono
    buffer_geometry = point_geometry.buffer(buffer_radius_degrees, segments)
    
    # Crear un nuevo polígono
    polygon = QgsFeature()
    polygon.setGeometry(buffer_geometry)
    polygon.setAttributes([magnitude])
    provider_polygon.addFeature(polygon)
    polygons.append(buffer_geometry)

# Combinar polígonos que se superponen
combined_geometry = QgsGeometry.unaryUnion(polygons)

# Crear un nuevo polígono combinado
combined_polygon = QgsFeature()
combined_polygon.setGeometry(combined_geometry)
combined_polygon.setAttributes(["Polígono combinado"])
provider_polygon.addFeature(combined_polygon)

# Crear rangos para colores dependiendo de la magnitud
ranges = [
    QgsRendererRange(0, 3, QgsFillSymbol.createSimple({"style": "solid", "color": "blue"}), "Bajo"),
    QgsRendererRange(3, 4, QgsFillSymbol.createSimple({"style": "solid", "color": "green"}), "Moderado"),
    QgsRendererRange(4, 5, QgsFillSymbol.createSimple({"style": "solid", "color": "yellow"}), "Medio"),
    QgsRendererRange(5, 6, QgsFillSymbol.createSimple({"style": "solid", "color": "orange"}), "Alto"),
    QgsRendererRange(6, 10, QgsFillSymbol.createSimple({"style": "solid", "color": "red"}), "Muy Alto"),
]

# Aplicar simbología basada en graduación
renderer = QgsGraduatedSymbolRenderer("Magnitud", ranges)
polygon_layer.setRenderer(renderer)

# Añadir la capa de polígonos al proyecto
QgsProject.instance().addMapLayer(polygon_layer)

print("Polígonos generados y añadidos al proyecto con simbología graduada según la magnitud.")
