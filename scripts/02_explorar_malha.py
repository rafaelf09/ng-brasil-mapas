import geopandas as gpd

gdf = gpd.read_file("data/raw/BR_Municipios_2022.shp")

print("Formato:", gdf.shape)
print("\nColunas:", gdf.columns.tolist())
print("\nPrimeiras linhas:")
print(gdf.head())
print("\nCRS (sistema de coordenadas):", gdf.crs)
print("\nTipo de geometria:")
print(gdf.geometry.geom_type.value_counts())
