import overpy
import geojson
import geopandas as gpd
from shapely.geometry import LineString


def query_overpass(bbox, key_value):
    # Query Overpass para vias com base no tipo especificado
    query = f"""
    [out:json][timeout:25];
    (
      way["{key_value}"]({bbox});
    );
    out body;
    >;
    out skel qt;
    """

    api = overpy.Overpass()

    try:
        result = api.query(query)
    except overpy.exception.OverpassTooManyRequests:
        print("Aguarde um momento e tente novamente.")
        return None
    except overpy.exception.OverpassRuntimeError as e:
        print(f"Erro na consulta: {e}")
        return None

    return result


def process_geojson(geojson_file):
    with open(geojson_file) as f:
        geojson_data = geojson.load(f)

    # Extrai a caixa delimitadora de todos os polígonos
    bboxes = []
    for feature in geojson_data['features']:
        coords = feature['geometry']['coordinates'][0]
        min_lon = min(coord[0] for coord in coords)
        max_lon = max(coord[0] for coord in coords)
        min_lat = min(coord[1] for coord in coords)
        max_lat = max(coord[1] for coord in coords)

        bbox = f"{min_lat},{min_lon},{max_lat},{max_lon}"
        bboxes.append(bbox)

    return bboxes


def save_to_shapefile(result, shapefile_path):
    data = []
    for way in result.ways:
        # Obtém as coordenadas dos nós
        coords = [(float(node.lon), float(node.lat)) for node in way.nodes]
        line = LineString(coords)

        # Cria um dicionário com as tags e geometria
        data.append({
            "name": way.tags.get('name', 'N/A'),
            "type": way.tags.get('highway', 'N/A'),
            "geometry": line
        })

    if data:
        # Cria um GeoDataFrame a partir da lista de dicionários
        gdf = gpd.GeoDataFrame(data, geometry='geometry', crs="EPSG:4326")  # Define CRS WGS84

        # Salva o GeoDataFrame como um arquivo shapefile
        gdf.to_file(shapefile_path, driver="ESRI Shapefile")
        print(f"Shapefile salvo com sucesso em {shapefile_path}")
    else:
        print("Nenhuma geometria encontrada para salvar no shapefile.")


def main(geojson_file, shapefile_path_prefix, key_value):
    # Processa o arquivo GeoJSON para obter a caixa delimitadora  de cada polígono
    bboxes = process_geojson(geojson_file)

    for i, bbox in enumerate(bboxes):
        # Faz a consulta na API do Overpass
        result = query_overpass(bbox, key_value)

        if result:
            # Define o caminho do shapefile para cada polígono
            shapefile_path = f"{shapefile_path_prefix}_polygon_{i + 1}.shp"
            # Salva o resultado em um shapefile
            save_to_shapefile(result, shapefile_path)


if __name__ == "__main__":
    # Insira o caminho do arquivo GeoJSON contendo os polígonos e o caminho de saída base para os shapefiles
    geojson_file = "caminho"
    shapefile_path_prefix = ""
    key_value = "highway"  # Mude conforme necessário

    main(geojson_file, shapefile_path_prefix, key_value)
