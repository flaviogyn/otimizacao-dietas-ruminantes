# Modelo de PL – Dieta de custo mínimo das vacas em lactação (GO_campo_dourado)

> Gerado por `Scripts/gerar_modelo_pl.py`. Não edite à mão: altere a planilha ou o script e gere de novo.

## 1. Escopo

- **Lote:** `lac_cow` (vacas em lactação), formulado para a **vaca média** do lote, base **1 dia**.
- **Padrão nutricional:** NASEM (`nutrient_standard` do `config.json`), com as mesmas restrições do otimizador de ração do RuFaS (`RUFAS/biophysical/animal/ration/ration_optimizer.py`).
- **Peso vivo médio:** 640,4 kg · **Consumo de MS estimado:** 24,752 kg/dia.

## 2. Variáveis de decisão

xᵢ = quantidade do alimento *i* na dieta, em **kg de matéria seca por vaca por dia** (xᵢ ≥ 0).

| Variável | Alimento | Tipo (RuFaS) | Custo cᵢ (R$/kg MS) | Preço (R$/t MN) |
|---|---|---|---|---|
| x18 | Feno de bermudagrass (Tifton) | Forage | 1,8207 | 1.700,00 |
| x44 | Milho grão moído seco | Conc | 1,2413 | 1.078,83 |
| x51 | Silagem de milho | Forage | 0,6988 | 247,08 |
| x94 | Feno capim-leguminosa | Forage | 2,5213 | 2.250,00 |
| x100 | Silagem capim-leguminosa | Forage | 2,7486 | 1.100,00 |
| x110 | Silagem de leguminosa | Forage | 2,5653 | 1.100,00 |
| x176 | Silagem de capim-sudão | Forage | 0,7851 | 247,08 |
| x301 | Premix mineral/vitamínico | Mineral | 12,2904 | 12.224,00 |
| x303 | Blend de subprodutos (conc. proteico) | Conc | 1,2159 | 901,11 |

Ficam **fora** do modelo do lote `lac_cow`:
- **x23 – farinha de sangue:** uso proibido para ruminantes no Brasil (IN MAPA nº 8/2004).
- **x202 – leite integral** e **x216 – starter:** alimentos exclusivos de bezerros (lote `calf`).

## 3. Função objetivo

Minimizar o custo diário da dieta por vaca (R$/vaca/dia):

$$\min Z = \sum_i c_i \, x_i$$

```
min Z = 1,8207·x18 + 1,2413·x44 + 0,6988·x51 + 2,5213·x94 + 2,7486·x100 + 2,5653·x110 + 0,7851·x176 + 12,2904·x301 + 1,2159·x303
```

## 4. Restrições

**R1a_consumo_MS_min** – Consumo de MS ≥ (1 − 0,30) × consumo estimado (kg MS/dia)  
*Origem no RuFaS:* `DMI_constraint_lower`

```
1,0000·x18 + 1,0000·x44 + 1,0000·x51 + 1,0000·x94 + 1,0000·x100 + 1,0000·x110 + 1,0000·x176 + 1,0000·x301 + 1,0000·x303  ≥  17,3267
```

**R1b_consumo_MS_max** – Consumo de MS ≤ (1 + 0,30) × consumo estimado (kg MS/dia)  
*Origem no RuFaS:* `DMI_constraint_upper`

```
1,0000·x18 + 1,0000·x44 + 1,0000·x51 + 1,0000·x94 + 1,0000·x100 + 1,0000·x110 + 1,0000·x176 + 1,0000·x301 + 1,0000·x303  ≤  32,1782
```

**R2_energia_liquida** – Energia líquida NASEM ≥ manutenção + lactação + crescimento + gestação (Mcal/dia)  
*Origem no RuFaS:* `NASEM_net_energy_constraint`

```
1,7953·x18 + 2,3165·x44 + 2,0709·x51 + 1,9188·x94 + 1,8844·x100 + 1,8534·x110 + 1,6394·x176 − 0,1875·x301 + 1,9763·x303  ≥  52,3437
```

**R3_PM_min_NDT** – Proteína metabolizável ≥ exigência, com proteína microbiana limitada pelo NDT (g/dia)  
*Origem no RuFaS:* `protein_constraint_lower (1º termo do min)`

```
63,8324·x18 + 99,1059·x44 + 71,1721·x51 + 71,7214·x94 + 70,6693·x100 + 81,4868·x110 + 70,9403·x176 + 4,7200·x301 + 326,3928·x303  ≥  2.662,1143
```

**R4_PM_min_PDR** – Proteína metabolizável ≥ exigência, com proteína microbiana limitada pela PDR (g/dia)  
*Origem no RuFaS:* `protein_constraint_lower (2º termo do min)`

```
67,8272·x18 + 58,5307·x44 + 50,2368·x51 + 94,8550·x94 + 106,1834·x100 + 123,9203·x110 + 56,9029·x176 + 4,7200·x301 + 265,0060·x303  ≥  2.662,1143
```

**R5_PM_max** – Proteína metabolizável ≤ 1,5 × exigência (g/dia)  
*Origem no RuFaS:* `protein_constraint_upper`

```
63,8324·x18 + 99,1059·x44 + 71,1721·x51 + 71,7214·x94 + 70,6693·x100 + 81,4868·x110 + 70,9403·x176 + 4,7200·x301 + 326,3928·x303  ≤  3.993,1715
```

**R6_calcio** – Cálcio digestível ≥ exigência (g/dia)  
*Origem no RuFaS:* `calcium_constraint`

```
1,4730·x18 + 0,2100·x44 + 0,7110·x51 + 1,8750·x94 + 2,6100·x100 + 3,7620·x110 + 1,3380·x176 + 146,5850·x301 + 2,5320·x303  ≥  66,9975
```

**R7_fosforo** – Fósforo digestível ≥ exigência (g/dia)  
*Origem no RuFaS:* `phosphorus_constraint`

```
1,2480·x18 + 2,1630·x44 + 1,4848·x51 + 2,1056·x94 + 2,1824·x100 + 2,2464·x110 + 1,7024·x176 + 18,5600·x301 + 5,1100·x303  ≥  63,4099
```

**R8_FDN_min** – FDN da dieta ≥ 25% da MS  
*Origem no RuFaS:* `NDF_constraint_lower`

```
40,4100·x18 − 15,2400·x44 + 15,9300·x51 + 29,6900·x94 + 26,2300·x100 + 18,2000·x110 + 41,6200·x176 − 24,8600·x301 − 1,1200·x303  ≥  0,0000
```

**R9_FDN_max** – FDN da dieta ≤ 45% da MS  
*Origem no RuFaS:* `NDF_constraint_upper`

```
20,4100·x18 − 35,2400·x44 − 4,0700·x51 + 9,6900·x94 + 6,2300·x100 − 1,8000·x110 + 21,6200·x176 − 44,8600·x301 − 21,1200·x303  ≤  0,0000
```

**R10_FDN_forragem** – FDN de forragem ≥ 15% da MS  
*Origem no RuFaS:* `forage_NDF_constraint`

```
50,4100·x18 − 15,0000·x44 + 25,9300·x51 + 39,6900·x94 + 36,2300·x100 + 28,2000·x110 + 51,6200·x176 − 15,0000·x301 − 15,0000·x303  ≥  0,0000
```

**R11_extrato_etereo** – Extrato etéreo da dieta ≤ 7% da MS  
*Origem no RuFaS:* `fat_constraint`

```
−5,0720·x18 − 3,1550·x44 − 4,0840·x51 − 3,6060·x94 − 2,9620·x100 − 4,1280·x110 − 4,3080·x176 − 6,9988·x301 − 1,7791·x303  ≤  0,0000
```

**Não negatividade:** xᵢ ≥ 0 para todo *i*. O limite superior do `NASEM_Comp.csv` (`limit` = 100 kg) nunca é atingido, porque Σxᵢ ≤ 32,178 kg.

## 5. Matriz de coeficientes (para o Solver)

| Restrição | x18 | x44 | x51 | x94 | x100 | x110 | x176 | x301 | x303 | Sentido | Lado direito |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Custo (Z)** | 1,8207 | 1,2413 | 0,6988 | 2,5213 | 2,7486 | 2,5653 | 0,7851 | 12,2904 | 1,2159 | min | — |
| R1a_consumo_MS_min | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | ≥ | 17,3267 |
| R1b_consumo_MS_max | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | ≤ | 32,1782 |
| R2_energia_liquida | 1,7953 | 2,3165 | 2,0709 | 1,9188 | 1,8844 | 1,8534 | 1,6394 | -0,1875 | 1,9763 | ≥ | 52,3437 |
| R3_PM_min_NDT | 63,8324 | 99,1059 | 71,1721 | 71,7214 | 70,6693 | 81,4868 | 70,9403 | 4,7200 | 326,3928 | ≥ | 2.662,1143 |
| R4_PM_min_PDR | 67,8272 | 58,5307 | 50,2368 | 94,8550 | 106,1834 | 123,9203 | 56,9029 | 4,7200 | 265,0060 | ≥ | 2.662,1143 |
| R5_PM_max | 63,8324 | 99,1059 | 71,1721 | 71,7214 | 70,6693 | 81,4868 | 70,9403 | 4,7200 | 326,3928 | ≤ | 3.993,1715 |
| R6_calcio | 1,4730 | 0,2100 | 0,7110 | 1,8750 | 2,6100 | 3,7620 | 1,3380 | 146,5850 | 2,5320 | ≥ | 66,9975 |
| R7_fosforo | 1,2480 | 2,1630 | 1,4848 | 2,1056 | 2,1824 | 2,2464 | 1,7024 | 18,5600 | 5,1100 | ≥ | 63,4099 |
| R8_FDN_min | 40,4100 | -15,2400 | 15,9300 | 29,6900 | 26,2300 | 18,2000 | 41,6200 | -24,8600 | -1,1200 | ≥ | 0,0000 |
| R9_FDN_max | 20,4100 | -35,2400 | -4,0700 | 9,6900 | 6,2300 | -1,8000 | 21,6200 | -44,8600 | -21,1200 | ≤ | 0,0000 |
| R10_FDN_forragem | 50,4100 | -15,0000 | 25,9300 | 39,6900 | 36,2300 | 28,2000 | 51,6200 | -15,0000 | -15,0000 | ≥ | 0,0000 |
| R11_extrato_etereo | -5,0720 | -3,1550 | -4,0840 | -3,6060 | -2,9620 | -4,1280 | -4,3080 | -6,9988 | -1,7791 | ≤ | 0,0000 |

## 6. De onde vem cada coeficiente

| Coeficiente | Cálculo | Unidade |
|---|---|---|
| cᵢ | coluna I da planilha (`purchased_feed_cost`) | R$/kg MS |
| NEᵢ (R2) | 0,66 × EDᵢ NASEM, EDᵢ por `calculate_NASEM_digestible_energy` | Mcal/kg MS |
| PM (R3, R5) | 0,64 × 0,13 × 1000 × NDTᵢ × desconto + PNDRᵢ × dPNDRᵢ × 1000 + 0,4 × 11,8 (endógena) | g/kg MS |
| PM (R4) | 0,64 × 0,85 × 1000 × PDRᵢ + PNDRᵢ × dPNDRᵢ × 1000 + 0,4 × 11,8 (endógena) | g/kg MS |
| Caᵢ (R6) | digestibilidade × Ca%ᵢ × 10 (forragem 0,30; concentrado 0,60; mineral 0,95) | g/kg MS |
| Pᵢ (R7) | digestibilidade × P%ᵢ × 10 (forragem 0,64; concentrado 0,70; mineral 0,80) | g/kg MS |
| FDN, FDN de forragem, EE (R8–R11) | teor do alimento − limite em % (só forragens contam em R10) | % MS |

**Lados direitos:**

- R2: exigência de energia líquida = 12,671 (manutenção) + 31,052 (lactação) + 0,696 (crescimento) + 2,374 (gestação) = **46,793 Mcal**. Como o RuFaS desconta da energia digestível as perdas por metano (13,28 × 0,3383 kg CH₄) e por urina (0,0146 × 268,3 g N) = 8,410 Mcal, esse termo constante passa para o lado direito: 46,793 + 0,66 × 8,410.
- R1a/R1b: consumo estimado de 24,752 kg ± 30%.
- R3–R5: exigência de PM = 2.662,11 g; limite superior = 1,5 × exigência. A PM endógena do RuFaS (0,4 × 11,8 g por kg de MS) é proporcional ao consumo e por isso entra nos coeficientes, não no lado direito.
- R6, R7: Ca = 66,997 g e P = 63,410 g (o maior entre `P_req` e `P_req_process`).

## 7. Hipóteses e linearizações

O otimizador do RuFaS é **não linear** (SLSQP). Para virar um PL resolvível pelo Simplex:
1. **Restrições em % da MS reescritas na forma linear:** por exemplo, FDN ≥ 25% vira Σ(FDNᵢ − 25)·xᵢ ≥ 0. O consumo de MS pode variar na mesma faixa do RuFaS (±30%, R1a/R1b); as digestibilidades que dependem do consumo foram calculadas no consumo estimado (24,752 kg).
2. **Ponto de referência = ração média do caso base** (simulação de 1 ano). Os termos que dependem da dieta inteira foram calculados nesse ponto e tratados como constantes:
   - desconto de NDT por nível de consumo = 0,8805;
   - amido total da dieta (entra na digestibilidade da FDN) = 7,008 kg;
   - concentrado na dieta (entra na taxa de passagem da proteína) = 47,48%.
3. **PM com mínimo de dois termos:** a proteína microbiana do RuFaS é min(limite por NDT, limite por PDR). Exigir PM ≥ exigência com o mínimo equivale a exigir as duas restrições lineares R3 **e** R4. Para o limite superior (R5) foi usado o termo limitado pelo NDT, o que é uma condição suficiente.
4. **Exigências fixas** da vaca média: média das 9 formulações do caso base (`GO_campo_dourado_caso_base_saved_variables_csv_all_variables.txt_30-Oct-2026_Fri_18-46-10.csv`). Perdas de metano e N urinário: médias diárias do caso base.
5. **Observação sobre o RuFaS:** `calculate_NASEM_dNDF` usa `(total_starch − 26)`; a equação NASEM espera o amido em % da MS, mas o RuFaS passa em kg. O modelo reproduz o cálculo do RuFaS para que a solução seja coerente com o simulador.

## 8. Verificação

- O modelo é **viável** (montado com PuLP e resolvido com o CBC, *solver* padrão do PuLP).
- Na solução do PL, recalculando os termos não lineares com as funções do RuFaS, a energia líquida fica -0,16% e a PM 0,01% em relação ao valor do PL (erro da linearização).

## 9. Solução e sensibilidade

Custo ótimo: **R$ 24,3086/vaca/dia**, com 25,845 kg de MS.

| Variável | Alimento | kg MS/vaca/dia | % da MS | Custo reduzido (R$/kg MS) |
|---|---|---|---|---|
| x18 | Feno de bermudagrass (Tifton) | 0,000 | 0,0 | 1,0989 |
| x44 | Milho grão moído seco | 0,000 | 0,0 | 0,5046 |
| x51 | Silagem de milho | 19,188 | 74,2 | 0,0000 |
| x94 | Feno capim-leguminosa | 0,000 | 0,0 | 1,6840 |
| x100 | Silagem capim-leguminosa | 0,000 | 0,0 | 1,8381 |
| x110 | Silagem de leguminosa | 0,000 | 0,0 | 1,5340 |
| x176 | Silagem de capim-sudão | 0,000 | 0,0 | 0,1357 |
| x301 | Premix mineral/vitamínico | 0,253 | 1,0 | 0,0000 |
| x303 | Blend de subprodutos (conc. proteico) | 6,404 | 24,8 | 0,0000 |

| Restrição | Folga | Preço-sombra |
|---|---|---|
| R1a_consumo_MS_min | 8,518 | 0,00000 |
| R1b_consumo_MS_max | 6,334 | 0,00000 |
| R2_energia_liquida | 0,000 | 0,26463 |
| R3_PM_min_NDT | 794,797 | 0,00000 |
| R4_PM_min_PDR | 0,000 | 0,00181 |
| R5_PM_max | 536,260 | 0,00000 |
| R6_calcio | 0,000 | 0,08413 |
| R7_fosforo | 2,505 | 0,00000 |
| R8_FDN_min | 292,188 | 0,00000 |
| R9_FDN_max | 224,704 | 0,00000 |
| R10_FDN_forragem | 397,681 | 0,00000 |
| R11_extrato_etereo | 91,528 | 0,00000 |
