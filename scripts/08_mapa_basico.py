import pandas as pd
import json
import plotly.graph_objects as go

# 1. Ler o geojson das geometrias
with open("data/processed/municipios.geojson", encoding="utf-8") as f:
    geojson = json.load(f)

# 2. Ler os dados (NG por município) em CSV
df = pd.read_csv("data/processed/ng_dados.csv", dtype={"CD_MUN": str})

print("Linhas no CSV:", len(df))
print(df.head())

# 3. Montar o choropleth.
#    - geojson: a malha de polígonos
#    - locations: a coluna do df que corresponde ao "id" de cada feature
#      do geojson (aqui, CD_MUN)
#    - z: o valor numérico que vai definir a cor de cada município
#    - featureidkey: diz ao Plotly ONDE dentro do geojson está o id de
#      cada feature -- por padrão o geopandas salva como "properties.CD_MUN"
fig = go.Figure(go.Choropleth(
    geojson=geojson,
    locations=df["CD_MUN"],
    z=df["ng_medio"],
    featureidkey="properties.CD_MUN",
    colorscale="Viridis",
    marker_line_width=0.2,
    colorbar_title="NG médio<br>(raios/km²/ano)",
))

fig.update_geos(
    visible=False,
    fitbounds="locations",   # ajusta o zoom automaticamente para caber tudo
)

fig.update_layout(
    title="Densidade de Descargas Atmosféricas por Município - Brasil",
    margin=dict(t=50, b=10, l=10, r=10),
)

fig.write_html("output/mapa_basico.html")
print("\nMapa salvo em output/mapa_basico.html")
