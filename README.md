# Case: Clusterização Inteligente de Lojas & Calibragem de Metas (FP&A) — Aurora Varejo

🌐 **Simulador Web Interativo & Case Executivo:** [darlansandro.com.br/projeto_clusterizacao_lojas-pt.html](https://darlansandro.com.br/projeto_clusterizacao_lojas-pt.html)

Estudo de caso completo de **Aprendizado Não Supervisionado (CRISP-DM)** e **Controladoria Estratégica (FP&A)** para segmentar as **1.115 lojas** da rede Aurora Varejo a partir de **1.017.209 registros diários de vendas** (`01/01/2013` a `31/07/2015`) e dados cadastrais, substituindo a meta linear uniforme (`+5%`) por metas relativas calibradas entre pares comparáveis.

---

## 1. Pergunta de Negócio e Objetivos (Fase 1 — Business Understanding)
- **Pergunta Analítica:** *"Quais lojas são verdadeiramente comparáveis entre si e quem está performando abaixo dos seus pares?"*
- **4 Áreas Consumidoras:**
  1. **Comercial:** Metas justas por grupo de pares comparáveis e calibradas para o orçamento corporativo (`+5,00%`).
  2. **Trade Marketing:** Alocação de verbas promocionais onde há maior elasticidade observada (`efeito_promo`).
  3. **Supply Chain:** Adequação de sortimento e estoque de segurança à volatilidade e sazonalidade.
  4. **Expansão:** Enquadramento determinístico de lojas recém-inauguradas sem retreinar o modelo.

---

## 2. Os 5 Arquétipos Operacionais Descobertos (`K-Means`, $k=5$)

| Cluster | Arquétipo Comercial | Lojas | Venda Mediana (P50) | Venda Média/Dia | Ticket Médio | Efeito Promo | Volatilidade | Sazonalidade | Dist. Mediana |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | **Padrão Bairro** | 292 (26,2%) | R$ 5.476,37 | R$ 5.717,90 | R$ 8,43 | +45,53% | 27,31% | 8,41% | 840 m |
| **1** | **Destino & Isolada** | 414 (37,1%) | R$ 6.959,92 | R$ 7.129,44 | R$ 11,35 | +34,97% | 25,02% | 9,23% | 5.830 m |
| **2** | **Sazonal / Turística** | 65 (5,8%) | R$ 6.324,80 | R$ 6.463,29 | R$ 8,19 | +31,80% | 31,20% | 15,88% | 3.170 m |
| **3** | **Viciada em Promoção** | 165 (14,8%) | R$ 5.909,24 | R$ 6.038,79 | R$ 9,68 | +70,79% | 36,41% | 9,35% | 4.680 m |
| **4** | **Flagship / Alto Fluxo** | 179 (16,1%) | R$ 8.837,11 | R$ 9.545,08 | R$ 8,00 | +26,38% | 21,37% | 7,57% | 900 m |

---

## 3. Metodologia e Pipeline Técnico (Fases 2 a 6)
1. **Auditoria de Dados (`Data Understanding`):**
   - Filtro estrito de dias efetivamente abertos (`aberta == 1` $\rightarrow$ `844.392` registros operacionais ativos), evitando diluir a média diária pelos `172.817` dias de portas fechadas.
   - Identificação do hiato de **180 lojas ausentes** entre `01/07/2014` e `31/12/2014` (`935` lojas ativas no período), exigindo normalização anualizada da sazonalidade.
   - Imputação dos 3 nulos de `distancia_concorrente` pela mediana da rede (`2.330,0 m`).
2. **Engenharia de Features Unificada (`Data Preparation`):**
   - Função única `construir_base_lojas(treino, loja)` que consolida as 6 features contínuas do modelo:
     - `venda_media_dia` (porte diário operante)
     - `ticket_medio` ($\sum \text{faturamento} / \sum \text{clientes}$)
     - `efeito_promo` (lift observacional em dias com promoção vs. sem promoção)
     - `volatilidade` ($\text{CV} = \sigma / \mu$ diário)
     - `sazonalidade` (desvio padrão das médias mensais normalizadas pela média anual de cada loja)
     - `distancia_concorrente` (metros até o concorrente mais próximo)
   - Transformação `np.log1p` nas 6 variáveis + padronização `StandardScaler` (`SEED = 42`).
3. **Modelagem e Validação (`Modeling` & `Evaluation`):**
   - **Algoritmo Oficial:** `KMeans(n_clusters=5, n_init=20, random_state=42)` validado contra o Método do Cotovelo, Coeficiente de Silhueta (`0,2042`) e Clusterização Hierárquica de Ward.
   - **Estabilidade:** ARI de reordenação = **`0,9886`**; ARI médio em 10 subamostragens de 80% = **`0,9092`** ($\pm 0,0612$).
   - **Superioridade sobre o Baseline (`tipo_loja`):** Ganho de **10,2x** na variância explicada ($\eta^2$) de faturamento (**`28,33%`** vs **`2,78%`**), **6,9x** em efeito promocional (**`57,77%`** vs **`8,37%`**) e **30,3x** em volatilidade (**`60,83%`** vs **`2,01%`**).
4. **Implantação (`Deployment`):**
   - **Entrega 1:** Planilha executiva [`planilha_metas_comercial_varejo.xlsx`](./planilha_metas_comercial_varejo.xlsx) calibrada pelo fator ponderado `1,1916` para atingir exatos `+5,00%` na receita global da rede.
   - **Entrega 2:** Pipeline serializado [`modelo_clusterizacao_varejo.joblib`](./modelo_clusterizacao_varejo.joblib) (compactado em [`.zip`](./modelo_clusterizacao_varejo.zip)), script de inferência [`codigo.py`](./codigo.py) e base de teste [`lojas_novas_exemplo.csv`](./lojas_novas_exemplo.csv).

---

## 4. Como Executar Localmente
```bash
pip install -r requirements.txt
python codigo.py
```

---

## 5. Governança e Limitações Metodológicas
- **Dados Observacionais:** O indicador `efeito_promo` mede associação histórica (lift observacional), e não efeito causal isolado de calendário ou margem líquida.
- **Cenário Financeiro Bruto:** O gap anual de `R$ 203,75 milhões` (`R$ 50,94 milhões` no cenário realista de 25% de captura) representa um cenário teórico de receita bruta em 300 dias operacionais, devendo ser validado por supervisores regionais quanto a restrições físicas de loja.
