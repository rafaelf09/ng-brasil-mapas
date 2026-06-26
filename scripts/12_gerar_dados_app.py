import geopandas as gpd
import json

gdf = gpd.read_file("data/processed/dataset_final.gpkg", layer="municipios_ng")
gdf["CD_MUN"] = gdf["CD_MUN"].astype(str)

# --- 1. GeoJSON (só geometria + id) ---
geo_export = gdf[["CD_MUN", "geometry"]].copy()
geo_export.to_file("/tmp/temp_final.geojson", driver="GeoJSON")

with open("/tmp/temp_final.geojson", encoding="utf-8") as f:
    gj = json.load(f)

for feat in gj["features"]:
    feat["id"] = feat["properties"]["CD_MUN"]
    feat["properties"] = {}

with open("output/municipios.geojson", "w", encoding="utf-8") as f:
    json.dump(gj, f)

# --- 2. Dados por município ---
dados = gdf.drop(columns="geometry").set_index("CD_MUN").to_dict(orient="index")

# limpar NaN/None para JSON válido e garantir tipos nativos do Python
import math
for cod, info in dados.items():
    for k, v in info.items():
        if isinstance(v, float) and math.isnan(v):
            info[k] = None

with open("output/ng_dados.json", "w", encoding="utf-8") as f:
    json.dump(dados, f, ensure_ascii=False)

# --- 3. Lista de UFs presentes ---
NOMES_UF = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal",
    "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão",
    "MT": "Mato Grosso", "MS": "Mato Grosso do Sul", "MG": "Minas Gerais",
    "PA": "Pará", "PB": "Paraíba", "PR": "Paraná", "PE": "Pernambuco",
    "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima",
    "SC": "Santa Catarina", "SP": "São Paulo", "SE": "Sergipe",
    "TO": "Tocantins",
}
ufs_presentes = sorted(gdf["SIGLA_UF"].unique())
uf_lista = [{"sigla": uf, "nome": NOMES_UF[uf]} for uf in ufs_presentes]
uf_lista.sort(key=lambda x: x["nome"])

with open("output/uf_lista.json", "w", encoding="utf-8") as f:
    json.dump(uf_lista, f, ensure_ascii=False)

# --- 4. Bounding box de cada UF (para zoom do mapa) ---
bounds_uf = {}
for uf in gdf["SIGLA_UF"].unique():
    sub = gdf[gdf["SIGLA_UF"] == uf]
    minx, miny, maxx, maxy = sub.total_bounds
    bounds_uf[uf] = [round(minx, 3), round(miny, 3), round(maxx, 3), round(maxy, 3)]
minx, miny, maxx, maxy = gdf.total_bounds
bounds_uf["BR"] = [round(minx, 3), round(miny, 3), round(maxx, 3), round(maxy, 3)]

with open("output/uf_bounds.json", "w", encoding="utf-8") as f:
    json.dump(bounds_uf, f)

import os
print("Tamanhos finais:")
for arq in ["municipios.geojson", "ng_dados.json", "uf_lista.json", "uf_bounds.json"]:
    print(f"  {arq}: {os.path.getsize(f'output/{arq}') / 1e6:.2f} MB")

print("\nExemplo de dado de município:")
print(list(dados.items())[0])
