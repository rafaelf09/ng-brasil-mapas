import pandas as pd

# 1. Ler o CSV oficial por município (fonte de referência principal)
oficial = pd.read_csv("data/raw/Ng_Brasil_Municipios_Alfabetico.csv", sep=";",
                       encoding="utf-8")
oficial.columns = ["CD_MUN", "NM_MUN", "SIGLA_UF", "ng_oficial"]
oficial["CD_MUN"] = oficial["CD_MUN"].astype(str)

print("Municípios na tabela oficial do INPE:", len(oficial))
print(oficial.head())
print("\nEstatística do Ng oficial:")
print(oficial["ng_oficial"].describe())

# 2. Ler nosso resultado calculado (grid + spatial join)
import geopandas as gpd
nosso = gpd.read_file("data/processed/ng_por_municipio_final.gpkg", layer="ng_municipio")
nosso["CD_MUN"] = nosso["CD_MUN"].astype(str)

print("\nMunicípios no nosso cálculo:", len(nosso))

# 3. Juntar as duas fontes pelo código IBGE
comparacao = oficial.merge(
    nosso[["CD_MUN", "ng_medio", "ng_max"]],
    on="CD_MUN", how="outer", indicator=True
)

print("\nResultado do merge (registro de correspondência):")
print(comparacao["_merge"].value_counts())

so_oficial = comparacao[comparacao["_merge"] == "left_only"]
so_nosso = comparacao[comparacao["_merge"] == "right_only"]
print("\nMunicípios só na tabela oficial (sem correspondência no nosso):", len(so_oficial))
print("Municípios só no nosso cálculo (sem correspondência na oficial):", len(so_nosso))

# 4. Calcular a diferença entre nosso valor de referência e o oficial
ambos = comparacao[comparacao["_merge"] == "both"].copy()
ambos["diferenca"] = ambos["ng_max"] - ambos["ng_oficial"]
ambos["diferenca_abs"] = ambos["diferenca"].abs()

print("\nEstatística da diferença (nosso ng_referencia - oficial):")
print(ambos["diferenca"].describe())

print("\nMaiores divergências (top 10):")
print(ambos.nlargest(10, "diferenca_abs")[
    ["NM_MUN", "SIGLA_UF", "ng_oficial", "ng_max", "ng_medio", "diferenca"]
])

comparacao.to_csv("data/processed/comparacao_fontes.csv", index=False)
print("\nSalvo em data/processed/comparacao_fontes.csv")
