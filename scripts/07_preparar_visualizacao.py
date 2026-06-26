import geopandas as gpd
import json

# 1. Ler o resultado final do pipeline de dados
gdf = gpd.read_file("data/processed/ng_por_municipio_final.gpkg", layer="ng_municipio")

print("Municípios:", len(gdf))
print("Colunas:", gdf.columns.tolist())

# 2. O Plotly precisa que cada feature do GeoJSON tenha um "id" -- vamos
#    usar o código IBGE do município (CD_MUN) para isso, e também vamos
#    simplificar as geometrias (reduzir a quantidade de pontos dos
#    polígonos), porque sem isso o arquivo fica pesado demais para
#    carregar rápido num navegador.
gdf["CD_MUN"] = gdf["CD_MUN"].astype(str)

print("\nNúmero médio de pontos por polígono ANTES de simplificar:")
print(gdf.geometry.apply(lambda g: len(g.exterior.coords) if g.geom_type == "Polygon" else sum(len(p.exterior.coords) for p in g.geoms)).mean())

# simplify(tolerance) reduz a quantidade de vértices dos polígonos,
# mantendo a forma geral. O valor está em graus (mesmo CRS, EPSG:4326).
gdf["geometry"] = gdf.geometry.simplify(0.01, preserve_topology=True)

print("\nNúmero médio de pontos por polígono DEPOIS de simplificar:")
print(gdf.geometry.apply(lambda g: len(g.exterior.coords) if g.geom_type == "Polygon" else sum(len(p.exterior.coords) for p in g.geoms)).mean())

# 3. Exportar GeoJSON (só geometria + id)
geo_export = gdf[["CD_MUN", "geometry"]].copy()
geo_export.to_file("data/processed/municipios.geojson", driver="GeoJSON")

# 4. Exportar os dados (sem geometria) separadamente, em CSV --
#    isso o Plotly/pandas vai usar para colorir o mapa
dados = gdf.drop(columns="geometry")
dados.to_csv("data/processed/ng_dados.csv", index=False)

import os
print("\nTamanho do geojson:", os.path.getsize("data/processed/municipios.geojson") / 1e6, "MB")
print("Tamanho do csv:", os.path.getsize("data/processed/ng_dados.csv") / 1e6, "MB")
