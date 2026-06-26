import geopandas as gpd
import json

gdf = gpd.read_file("data/processed/ng_por_municipio_final.gpkg", layer="ng_municipio")
gdf["CD_MUN"] = gdf["CD_MUN"].astype(str)

# Simplificação (mesma lógica do script 07, repetida aqui porque este
# script vai ser a fonte única de verdade para a visualização)
gdf["geometry"] = gdf.geometry.simplify(0.01, preserve_topology=True)

# --- 1. GeoJSON só com id + geometria (dados ficam de fora, no JSON leve) ---
geo_export = gdf[["CD_MUN", "geometry"]].copy()
geo_export.to_file("/tmp/temp.geojson", driver="GeoJSON")

with open("/tmp/temp.geojson", encoding="utf-8") as f:
    gj = json.load(f)

# Plotly (e nosso JS) vai usar feature["id"] diretamente, então copiamos
# o CD_MUN de dentro de "properties" para o nível "id" de cada feature.
for feat in gj["features"]:
    feat["id"] = feat["properties"]["CD_MUN"]
    feat["properties"] = {}  # esvazia -- os dados reais vão no JSON separado

with open("data/processed/municipios.geojson", "w", encoding="utf-8") as f:
    json.dump(gj, f)

# --- 2. Dados por município, em dicionário indexado pelo CD_MUN ---


dados = gdf[["CD_MUN", "NM_MUN", "SIGLA_UF", "ng_medio", "ng_min", "ng_max", "n_pontos"]].copy()

# Ng oficial de referência para uso em projeto de SPDA/aterramento:
# usamos o MÁXIMO observado entre os pontos do grid dentro do município,
# por ser a abordagem conservadora (mais segura) recomendada para
# dimensionamento, em vez da média. Arredondado para 1 casa decimal,
# seguindo o formato de apresentação da NBR 5419-3.
dados["ng_referencia"] = dados["ng_max"].round(1)

# mantemos média e mínimo arredondados também, como informação
# complementar/contexto (não são os valores usados no cálculo)
dados["ng_medio"] = dados["ng_medio"].round(1)
dados["ng_min"] = dados["ng_min"].round(1)
dados["ng_max"] = dados["ng_max"].round(1)
dados["n_pontos"] = dados["n_pontos"].astype(int)

dados_dict = dados.set_index("CD_MUN").to_dict(orient="index")

with open("data/processed/ng_dados.json", "w", encoding="utf-8") as f:
    json.dump(dados_dict, f, ensure_ascii=False)

# --- 3. Lista de estados (sigla -> nome completo) ---
# O shapefile do IBGE só trouxe a sigla (SIGLA_UF). Vamos mapear
# manualmente para o nome completo -- é uma lista fixa de 27 itens,
# não vale a pena buscar isso em outra fonte externa.
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
print("UFs encontradas nos dados:", len(ufs_presentes))

ufs_sem_nome = [uf for uf in ufs_presentes if uf not in NOMES_UF]
print("UFs sem nome mapeado (deveria ser vazio):", ufs_sem_nome)

uf_lista = [{"sigla": uf, "nome": NOMES_UF[uf]} for uf in ufs_presentes]
uf_lista.sort(key=lambda x: x["nome"])

with open("data/processed/uf_lista.json", "w", encoding="utf-8") as f:
    json.dump(uf_lista, f, ensure_ascii=False)

import os
print("\nTamanhos finais:")
print("geojson:", os.path.getsize("data/processed/municipios.geojson") / 1e6, "MB")
print("dados:", os.path.getsize("data/processed/ng_dados.json") / 1e6, "MB")
print("uf_lista:", os.path.getsize("data/processed/uf_lista.json") / 1e6, "MB")
