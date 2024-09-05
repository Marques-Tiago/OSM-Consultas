import os
import geopandas as gpd
import pandas as pd

def merge_shapefiles(input_directory, output_shapefile):
    # Obtém uma lista de todos os arquivos shapefile no diretório de entrada
    shapefiles = [os.path.join(input_directory, f) for f in os.listdir(input_directory) if f.endswith('.shp')]

    if not shapefiles:
        print("Nenhum shapefile encontrado no diretório.")
        return

    # Lê o primeiro shapefile e inicializa o GeoDataFrame
    gdf = gpd.read_file(shapefiles[0])

    # Concatena todos os shapefiles
    for shp in shapefiles[1:]:
        gdf_next = gpd.read_file(shp)
        gdf = pd.concat([gdf, gdf_next], ignore_index=True)

    # Salva o GeoDataFrame combinado como um novo shapefile
    gdf.to_file(output_shapefile, driver="ESRI Shapefile")
    print(f"Shapefiles combinados salvos com sucesso em {output_shapefile}")

# Caminho para o diretório contendo os shapefiles a serem combinados
input_directory = ""
# Caminho do shapefile combinado de saída
output_shapefile = ""

merge_shapefiles(input_directory, output_shapefile)