# Densidade de Descargas Atmosféricas (Ng) por Município — Brasil

Ferramenta de consulta geoespacial do índice **Ng** (densidade de descargas atmosféricas, raios/km²/ano) por município brasileiro, voltada para uso em projetos de **SPDA** (Sistema de Proteção contra Descargas Atmosféricas) e aterramento, conforme a **NBR 5419-2:2026** (vigente).

O projeto nasceu da vontade de facilitar o acesso público a esse dado — hoje disperso em tabelas extensas e mapas pouco interativos — para técnicos, engenheiros e qualquer pessoa interessada no assunto, através de um mapa simples e gratuito de consulta.

## O que o projeto faz

- Disponibiliza um mapa interativo (`output/app.html`) com seletor de Estado → Município
- Para cada município, exibe o **Ng oficial vigente** (NBR 5419-2:2026, Anexo F)
- Documenta e compara essa fonte com um cálculo geoespacial próprio, construído a partir de um grid histórico de descargas (1988–2011)

## Descoberta técnica: duas gerações de dados de Ng

Durante a construção do projeto, identifiquei que existem **duas gerações distintas** de mapeamento de Ng no Brasil:

| | Geração antiga (NBR 5419:2015) | Geração atual (NBR 5419-2:2026) |
|---|---|---|
| Fonte | Sensor LIS / satélite TRMM (NASA), 1988–2011 | LIS + rede de detecção de superfície BrasilDAT, calibração ampliada |
| Resolução | Grid de 0,25° x 0,25° (interpolação IDW) | Valor único por município (máximo observado no território) |
| Faixa de valores | ~0,5 a 19 raios/km²/ano | 2 a 32 raios/km²/ano (valores pares) |
| Responsável | INPE | INPE/DISSM + UFMT (PPGFA/NIEPE) |

A atualização eleva significativamente os valores de Ng em diversas regiões (ex: São Paulo de 11 para 22, Salvador de 0,5 para 4), refletindo maior precisão de detecção. Reproduzi esse achado construindo meu próprio pipeline a partir da fonte de dados antiga (grid 0,25°) e comparando o resultado com a tabela oficial do Anexo F — a diferença observada (sistematicamente negativa, entre -0,8 e -17 raios/km²/ano) é consistente com a mudança de metodologia documentada pela ABNT/INPE.

**O app usa a fonte vigente (NBR 5419-2:2026) como valor de referência principal.**

## Aviso técnico

Os valores de Ng aqui exibidos são uma ferramenta de referência rápida, derivada de dados públicos do INPE. Para uso formal em laudo técnico ou projeto de SPDA, **confirme sempre o valor diretamente no Anexo F da NBR 5419-2:2026 vigente** — este projeto não substitui a consulta normativa oficial.

## Estrutura do pipeline

| Script | O que faz |
|---|---|
| `01_explorar_dados.py` | Exploração inicial do grid de pontos (Excel) |
| `02_explorar_malha.py` | Leitura e inspeção da malha de municípios do IBGE |
| `03_criar_pontos.py` | Conversão do grid (lat/lon) em GeoDataFrame de pontos |
| `04_spatial_join.py` | Cruzamento espacial pontos × polígonos de município |
| `05_agregar_municipio.py` | Agregação do Ng por município (média, min, máx) |
| `06_preencher_vazios.py` | Preenchimento de municípios sem ponto interno (vizinho mais próximo, CRS métrico) |
| `07_preparar_visualizacao.py` / `08_mapa_basico.py` | Primeiros experimentos de visualização com Plotly (Python puro) |
| `09_preparar_dados_js.py` | Preparação de dados para visualização via JavaScript |
| `10_validar_fontes.py` | Comparação entre o cálculo próprio e a fonte oficial NBR 5419-2:2026 |
| `11_consolidar_dataset_final.py` | Consolidação do dataset final (geometria + Ng oficial + Ng histórico) |
| `12_gerar_dados_app.py` | Geração dos arquivos finais (`.geojson` / `.json`) usados pelo app |

## Como reproduzir

### 1. Ambiente

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

No macOS, o `geopandas` depende de bibliotecas de sistema (GDAL/GEOS/PROJ):

```bash
brew install gdal
```

### 2. Dados brutos (não incluídos no repositório)

| Arquivo | Fonte |
|---|---|
| Malha de municípios (`BR_Municipios_2022.shp` e correlatos) | [Malhas Territoriais — IBGE](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais.html) |
| Grid histórico de Ng (`tabela_ng_025x025_br.txt`) | [Catálogo de metadados — INPE](http://dataserver.cptec.inpe.br/dataserver_raio/tabela_ng/) |
| Tabela oficial de Ng por município (NBR 5419-2:2026) | INPE/DISSM + UFMT (Anexo F da NBR 5419-2:2026) |

Coloque os arquivos baixados em `data/raw/`.

### 3. Rodar o pipeline

```bash
python3 scripts/01_explorar_dados.py
python3 scripts/02_explorar_malha.py
# ... (em ordem, até o 12)
```

### 4. Visualizar o app

```bash
cd output
python3 -m http.server 8000
```

Acesse `http://localhost:8000/app.html`.

## Stack

- **Python**: pandas, geopandas, shapely, openpyxl
- **Visualização**: Plotly.js (CDN), HTML/CSS/JS vanilla
- **Geoprocessamento**: spatial join (`predicate="within"`), `sjoin_nearest` com CRS métrico (EPSG:5880) para preenchimento de vazios
- **CRS**: reprojeção entre SIRGAS2000 (EPSG:4674, padrão IBGE) e WGS84 (EPSG:4326)

## Autor

Rafael Fernandes
