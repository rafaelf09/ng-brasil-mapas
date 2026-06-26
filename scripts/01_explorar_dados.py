import pandas as pd

df = pd.read_excel("data/raw/coordenadas-NG.xlsx")

print("Formato (linhas, colunas):", df.shape)
print("\nColunas:", df.columns.tolist())
print("\nPrimeiras linhas:")
print(df.head())
print("\nTipos de dado:")
print(df.dtypes)
print("\nEstatísticas descritivas:")
print(df.describe())

print("\n--- Checando regularidade do grid ---")
lons_unicos = sorted(df["Longitude"].unique())
lats_unicos = sorted(df["Latitude"].unique())

print("Longitudes únicas:", len(lons_unicos))
print("Latitudes únicas:", len(lats_unicos))
print("Produto (lon x lat):", len(lons_unicos) * len(lats_unicos))
print("Total de pontos no arquivo:", len(df))

import numpy as np
passo_lon = np.diff(lons_unicos)
passo_lat = np.diff(lats_unicos)
print("\nPasso entre longitudes - min/max:", passo_lon.min(), passo_lon.max())
print("Passo entre latitudes - min/max:", passo_lat.min(), passo_lat.max())
