import geopandas as gpd
import pandas as pd

# 1. Malha de municípios (geometria), já em EPSG:4326
municipios = gpd.read_file("data/raw/BR_Municipios_2022.shp").to_crs("EPSG:4326")
municipios["CD_MUN"] = municipios["CD_MUN"].astype(str)
municipios["geometry"] = municipios.geometry.simplify(0.01, preserve_topology=True)

# 2. Ng oficial -- NBR 5419-2:2026 (Anexo F), fonte: INPE/DISSM + UFMT
#    Valor único por município = máximo observado no território (norma vigente)
oficial = pd.read_csv("data/raw/Ng_Brasil_Municipios_Alfabetico.csv", sep=";", encoding="utf-8")
oficial.columns = ["CD_MUN", "NM_MUN", "SIGLA_UF", "ng_nbr5419_2026"]
oficial["CD_MUN"] = oficial["CD_MUN"].astype(str)

# 3. Nosso cálculo histórico (grid LIS/TRMM 1988-2011, base da NBR 5419:2015)
#    -- mantido como contexto/comparação, não como valor de referência principal
nosso = gpd.read_file("data/processed/ng_por_municipio_final.gpkg", layer="ng_municipio")
nosso["CD_MUN"] = nosso["CD_MUN"].astype(str)
nosso_simples = nosso[["CD_MUN", "ng_medio", "ng_max"]].rename(
    columns={"ng_medio": "ng_2015_medio", "ng_max": "ng_2015_max"}
)
nosso_simples["ng_2015_medio"] = nosso_simples["ng_2015_medio"].round(1)
nosso_simples["ng_2015_max"] = nosso_simples["ng_2015_max"].round(1)

# 4. Consolidar tudo num único GeoDataFrame final
final = municipios.merge(oficial[["CD_MUN", "ng_nbr5419_2026"]], on="CD_MUN", how="left")
final = final.merge(nosso_simples, on="CD_MUN", how="left")

print("Total de municípios:", len(final))
print("Sem Ng oficial 2026:", final["ng_nbr5419_2026"].isna().sum())
print("Sem Ng histórico 2015 (nosso cálculo):", final["ng_2015_medio"].isna().sum())

print("\nAmostra final:")
print(final[["CD_MUN", "NM_MUN", "SIGLA_UF", "ng_nbr5419_2026", "ng_2015_max", "ng_2015_medio"]].head())

final = final.rename(columns={"AREA_KM2": "area_km2"})
final = final[["CD_MUN", "NM_MUN", "SIGLA_UF", "area_km2",
               "ng_nbr5419_2026", "ng_2015_max", "ng_2015_medio", "geometry"]]

final.to_file("data/processed/dataset_final.gpkg", layer="municipios_ng", driver="GPKG")
print("\nSalvo em data/processed/dataset_final.gpkg")
