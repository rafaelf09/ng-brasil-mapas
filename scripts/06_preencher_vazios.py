import geopandas as gpd
import pandas as pd

resultado = gpd.read_file("data/processed/ng_por_municipio.gpkg", layer="ng_municipio")
pontos = gpd.read_file("data/processed/pontos_ng.gpkg", layer="pontos")

sem_dado = resultado[resultado["ng_medio"].isna()].copy()
com_dado = resultado[resultado["ng_medio"].notna()].copy()
print("Municípios sem dado a preencher:", len(sem_dado))

# CRS projetado em metros para o Brasil: EPSG:5880 (SIRGAS 2000 / Brazil
# Polyconic) -- agora sim distância vai ser medida em metros de verdade,
# não em graus distorcidos.
CRS_METRICO = "EPSG:5880"

centroides = sem_dado.copy()
centroides["geometry"] = centroides.to_crs(CRS_METRICO).geometry.centroid
centroides = centroides.set_crs(CRS_METRICO, allow_override=True).to_crs("EPSG:4326")

pontos_metrico = pontos.to_crs(CRS_METRICO)
centroides_metrico = centroides.to_crs(CRS_METRICO)

preenchido = gpd.sjoin_nearest(centroides_metrico, pontos_metrico, how="left", distance_col="dist_metros")
preenchido["dist_km"] = preenchido["dist_metros"] / 1000

print("\nDistância (em km) até o ponto mais próximo - estatística:")
print(preenchido["dist_km"].describe())

print("\n--- Investigando os 5 casos mais distantes ---")
top5 = preenchido.nlargest(5, "dist_km")[["NM_MUN", "SIGLA_UF", "dist_km", "Dens_km2_ano"]]
print(top5)

# Preencher os valores
sem_dado = sem_dado.set_index("CD_MUN")
preenchido_idx = preenchido.set_index("CD_MUN")

sem_dado.loc[preenchido_idx.index, "ng_medio"] = preenchido_idx["Dens_km2_ano"]
sem_dado.loc[preenchido_idx.index, "ng_min"] = preenchido_idx["Dens_km2_ano"]
sem_dado.loc[preenchido_idx.index, "ng_max"] = preenchido_idx["Dens_km2_ano"]
sem_dado.loc[preenchido_idx.index, "n_pontos"] = 1
sem_dado = sem_dado.reset_index()

final = pd.concat([com_dado, sem_dado], ignore_index=True)
final = gpd.GeoDataFrame(final, geometry="geometry", crs=resultado.crs)

print("\nTotal final:", len(final))
print("Ainda sem dado?", final["ng_medio"].isna().sum())

final.to_file("data/processed/ng_por_municipio_final.gpkg", layer="ng_municipio", driver="GPKG")
print("\nSalvo em data/processed/ng_por_municipio_final.gpkg")
