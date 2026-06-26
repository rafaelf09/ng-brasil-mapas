import pandas as pd
import geopandas as gpd

# 1. Ler o Excel original (continua sendo um DataFrame comum, sem geometria)
df = pd.read_excel("data/raw/coordenadas-NG.xlsx")

# 2. Criar a geometria: cada linha (lon, lat) se torna um ponto.
#    gpd.points_from_xy é um atalho que cria objetos shapely.Point
#    a partir de duas colunas numéricas.
geometria = gpd.points_from_xy(df["Longitude"], df["Latitude"])

# 3. Montar o GeoDataFrame, dizendo explicitamente que esses pontos
#    estão no sistema WGS84 (EPSG:4326) -- é o mesmo que dizer
#    "essas coordenadas seguem o padrão GPS".
pontos = gpd.GeoDataFrame(df, geometry=geometria, crs="EPSG:4326")

print("Pontos criados:", len(pontos))
print(pontos.head())
print("CRS dos pontos:", pontos.crs)

# Salvar para reaproveitar nos próximos scripts sem reler o Excel
pontos.to_file("data/processed/pontos_ng.gpkg", layer="pontos", driver="GPKG")
print("\nSalvo em data/processed/pontos_ng.gpkg")

