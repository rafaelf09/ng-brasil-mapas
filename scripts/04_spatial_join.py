import geopandas as gpd

# 1. Ler a malha de municípios (ainda em SIRGAS2000 / EPSG:4674)
municipios = gpd.read_file("data/raw/BR_Municipios_2022.shp")
print("Municípios lidos:", len(municipios), "| CRS original:", municipios.crs)

# 2. Reprojetar para WGS84 (EPSG:4326), mesmo CRS dos nossos pontos.
#    .to_crs() recalcula as coordenadas matematicamente -- não é
#    apenas "trocar o rótulo", é uma conversão real (ainda que aqui
#    a diferença numérica seja mínima, como vimos).
municipios = municipios.to_crs("EPSG:4326")
print("CRS após reprojeção:", municipios.crs)

# 3. Ler os pontos NG que já preparamos
pontos = gpd.read_file("data/processed/pontos_ng.gpkg", layer="pontos")
print("Pontos NG:", len(pontos), "| CRS:", pontos.crs)

# 4. SPATIAL JOIN: para cada ponto, descobrir dentro de qual polígono
#    de município ele cai. predicate="within" = "o ponto está dentro
#    do polígono?". how="inner" = descarta pontos que não caem em
#    nenhum município (ex: pontos no oceano, fora do território).
join = gpd.sjoin(pontos, municipios, how="inner", predicate="within")

print("\nPontos que caíram dentro de algum município:", len(join), "de", len(pontos))
print("Pontos descartados (fora de qualquer município, ex: oceano):", len(pontos) - len(join))

print("\nAmostra do resultado do join:")
print(join[["Longitude", "Latitude", "Dens_km2_ano", "CD_MUN", "NM_MUN", "SIGLA_UF"]].head())

# Salvar o resultado intermediário
join.to_file("data/processed/pontos_com_municipio.gpkg", layer="join", driver="GPKG")
print("\nSalvo em data/processed/pontos_com_municipio.gpkg")
