import geopandas as gpd

# 1. Ler o resultado do join (pontos já com município atrelado)
join = gpd.read_file("data/processed/pontos_com_municipio.gpkg", layer="join")

# 2. Agrupar por município e calcular estatísticas do NG.
#    Aqui usamos groupby do pandas (geopandas herda esse método),
#    operando sobre a coluna de valor (Dens_km2_ano).
agregado = join.groupby("CD_MUN").agg(
    NM_MUN=("NM_MUN", "first"),
    SIGLA_UF=("SIGLA_UF", "first"),
    ng_medio=("Dens_km2_ano", "mean"),
    ng_min=("Dens_km2_ano", "min"),
    ng_max=("Dens_km2_ano", "max"),
    n_pontos=("Dens_km2_ano", "count"),
).reset_index()

print("Municípios com pelo menos 1 ponto do grid:", len(agregado))
print("\nAmostra:")
print(agregado.head())
print("\nEstatística de quantos pontos cada município tem (n_pontos):")
print(agregado["n_pontos"].describe())

# 3. Ler a malha de municípios novamente (precisamos da geometria
#    completa de TODOS os municípios, não só dos que têm ponto)
municipios = gpd.read_file("data/raw/BR_Municipios_2022.shp").to_crs("EPSG:4326")

# 4. Juntar a geometria com as estatísticas agregadas.
#    how="left" a partir de municipios garante que TODOS os 5572
#    municípios apareçam, mesmo os que não receberam nenhum ponto.
resultado = municipios.merge(agregado.drop(columns=["NM_MUN", "SIGLA_UF"]),
                              on="CD_MUN", how="left")

sem_dados = resultado["ng_medio"].isna().sum()
print(f"\nMunicípios SEM nenhum ponto do grid dentro: {sem_dados}")

resultado.to_file("data/processed/ng_por_municipio.gpkg", layer="ng_municipio", driver="GPKG")
print("\nSalvo em data/processed/ng_por_municipio.gpkg")
