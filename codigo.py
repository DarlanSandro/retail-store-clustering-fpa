from pathlib import Path
import joblib
import numpy as np
import pandas as pd

# Resolve diretório base (compatível com script local e células interativas como Google Colab)
BASE_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
CAMINHO_MODELO = BASE_DIR / "modelo_clusterizacao_varejo.joblib"
CAMINHO_CSV = BASE_DIR / "lojas_novas_exemplo.csv"

# 1. Carregar o artefato do pipeline treinado
pipeline_carregado = joblib.load(CAMINHO_MODELO)

# Extraindo componentes do pipeline
escalador_treinado = pipeline_carregado["escalador"]
modelo_kmeans_treinado = pipeline_carregado["modelo_kmeans"]
colunas_modelo = pipeline_carregado["colunas_modelo"]
nomes_clusters = pipeline_carregado["nomes_clusters"]

# 2. Carregar o arquivo com as novas lojas e validar schema e domínio do log1p
df_novas_lojas = pd.read_csv(CAMINHO_CSV)

colunas_faltantes = set(colunas_modelo) - set(df_novas_lojas.columns)
if colunas_faltantes:
    raise ValueError(f"Colunas obrigatórias ausentes no CSV: {sorted(colunas_faltantes)}")
if df_novas_lojas[colunas_modelo].isnull().any().any():
    raise ValueError("O arquivo de entrada contém valores nulos nas variáveis do modelo.")
if (df_novas_lojas[colunas_modelo] <= -1.0).any().any():
    raise ValueError("Valores <= -1.0 violam o domínio matemático da transformação log1p.")

# 3. Aplicar a transformação logarítmica log1p nas features
df_novas_log = df_novas_lojas[colunas_modelo].copy()
df_novas_log = np.log1p(df_novas_log)

# 4. Escalonar utilizando o Scaler pré-treinado (SOMENTE .transform())
matriz_novas_escalada = escalador_treinado.transform(df_novas_log)

# 5. Predizer o cluster sem retreinar o modelo (SOMENTE .predict())
df_novas_lojas["cluster_predito"] = modelo_kmeans_treinado.predict(matriz_novas_escalada)
df_novas_lojas["nome_cluster_predito"] = df_novas_lojas["cluster_predito"].map(nomes_clusters)

# Exibição dos resultados das novas lojas
print("=== CLASSIFICAÇÃO DAS NOVAS LOJAS ===")
print(df_novas_lojas[["loja", "venda_media_dia", "cluster_predito", "nome_cluster_predito"]].to_string(index=False))
