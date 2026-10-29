# Modelo de PL – Dieta de custo mínimo das vacas em lactação (GO_campo_dourado)

> Gerado por `otimizacao/gerar_modelo_pl.py`. Não edite à mão: altere a planilha ou o script e gere de novo.

## 1. Escopo

- **Lote:** `lac_cow` (vacas em lactação), formulado para a **vaca média** do lote, base **1 dia**.
- **Padrão nutricional:** NASEM (`nutrient_standard` do `config.json`), com as mesmas restrições do otimizador de ração do RuFaS (`RUFAS/biophysical/animal/ration/ration_optimizer.py`).
- **Peso vivo médio:** 640,5 kg · **Consumo de MS estimado:** 25,187 kg/dia.

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
1,0000·x18 + 1,0000·x44 + 1,0000·x51 + 1,0000·x94 + 1,0000·x100 + 1,0000·x110 + 1,0000·x176 + 1,0000·x301 + 1,0000·x303  ≥  17,6309
```

**R1b_consumo_MS_max** – Consumo de MS ≤ (1 + 0,30) × consumo estimado (kg MS/dia)  
*Origem no RuFaS:* `DMI_constraint_upper`

```
1,0000·x18 + 1,0000·x44 + 1,0000·x51 + 1,0000·x94 + 1,0000·x100 + 1,0000·x110 + 1,0000·x176 + 1,0000·x301 + 1,0000·x303  ≤  32,7431
```

**R2_energia_liquida** – Energia líquida NASEM ≥ manutenção + lactação + crescimento + gestação (Mcal/dia)  
*Origem no RuFaS:* `NASEM_net_energy_constraint`

```
1,7944·x18 + 2,3151·x44 + 2,0698·x51 + 1,9181·x94 + 1,8837·x100 + 1,8528·x110 + 1,6386·x176 − 0,1875·x301 + 1,9758·x303  ≥  53,8518
```

**R3_PM_min_NDT** – Proteína metabolizável ≥ exigência, com proteína microbiana limitada pelo NDT (g/dia)  
*Origem no RuFaS:* `protein_constraint_lower (1º termo do min)`

```
63,9058·x18 + 99,2484·x44 + 71,2015·x51 + 71,8046·x94 + 70,7367·x100 + 81,5925·x110 + 70,9732·x176 + 4,7200·x301 + 326,3994·x303  ≥  2.742,9400
```

**R4_PM_min_PDR** – Proteína metabolizável ≥ exigência, com proteína microbiana limitada pela PDR (g/dia)  
*Origem no RuFaS:* `protein_constraint_lower (2º termo do min)`

```
67,8385·x18 + 58,5653·x44 + 50,2421·x51 + 94,8725·x94 + 106,1974·x100 + 123,9429·x110 + 56,9032·x176 + 4,7200·x301 + 265,0060·x303  ≥  2.742,9400
```

**R5_PM_max** – Proteína metabolizável ≤ 1,5 × exigência (g/dia)  
*Origem no RuFaS:* `protein_constraint_upper`

```
63,9058·x18 + 99,2484·x44 + 71,2015·x51 + 71,8046·x94 + 70,7367·x100 + 81,5925·x110 + 70,9732·x176 + 4,7200·x301 + 326,3994·x303  ≤  4.114,4100
```

**R6_calcio** – Cálcio digestível ≥ exigência (g/dia)  
*Origem no RuFaS:* `calcium_constraint`

```
1,4730·x18 + 0,2100·x44 + 0,7110·x51 + 1,8750·x94 + 2,6100·x100 + 3,7620·x110 + 1,3380·x176 + 146,5850·x301 + 2,5320·x303  ≥  68,7830
```

**R7_fosforo** – Fósforo digestível ≥ exigência (g/dia)  
*Origem no RuFaS:* `phosphorus_constraint`

```
1,2480·x18 + 2,1630·x44 + 1,4848·x51 + 2,1056·x94 + 2,1824·x100 + 2,2464·x110 + 1,7024·x176 + 18,5600·x301 + 5,1100·x303  ≥  65,5170
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

**Não negatividade:** xᵢ ≥ 0 para todo *i*. O limite superior do `NASEM_Comp.csv` (`limit` = 100 kg) nunca é atingido, porque Σxᵢ ≤ 32,743 kg.

## 5. Matriz de coeficientes (para o Solver)

| Restrição | x18 | x44 | x51 | x94 | x100 | x110 | x176 | x301 | x303 | Sentido | Lado direito |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Custo (Z)** | 1,8207 | 1,2413 | 0,6988 | 2,5213 | 2,7486 | 2,5653 | 0,7851 | 12,2904 | 1,2159 | min | — |
| R1a_consumo_MS_min | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | ≥ | 17,6309 |
| R1b_consumo_MS_max | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | ≤ | 32,7431 |
| R2_energia_liquida | 1,7944 | 2,3151 | 2,0698 | 1,9181 | 1,8837 | 1,8528 | 1,6386 | -0,1875 | 1,9758 | ≥ | 53,8518 |
| R3_PM_min_NDT | 63,9058 | 99,2484 | 71,2015 | 71,8046 | 70,7367 | 81,5925 | 70,9732 | 4,7200 | 326,3994 | ≥ | 2.742,9400 |
| R4_PM_min_PDR | 67,8385 | 58,5653 | 50,2421 | 94,8725 | 106,1974 | 123,9429 | 56,9032 | 4,7200 | 265,0060 | ≥ | 2.742,9400 |
| R5_PM_max | 63,9058 | 99,2484 | 71,2015 | 71,8046 | 70,7367 | 81,5925 | 70,9732 | 4,7200 | 326,3994 | ≤ | 4.114,4100 |
| R6_calcio | 1,4730 | 0,2100 | 0,7110 | 1,8750 | 2,6100 | 3,7620 | 1,3380 | 146,5850 | 2,5320 | ≥ | 68,7830 |
| R7_fosforo | 1,2480 | 2,1630 | 1,4848 | 2,1056 | 2,1824 | 2,2464 | 1,7024 | 18,5600 | 5,1100 | ≥ | 65,5170 |
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

- R2: exigência de energia líquida = 12,686 (manutenção) + 32,450 (lactação) + 0,702 (crescimento) + 2,259 (gestação) = **48,097 Mcal**. Como o RuFaS desconta da energia digestível as perdas por metano (13,28 × 0,3493 kg CH₄) e por urina (0,0146 × 279,5 g N) = 8,719 Mcal, esse termo constante passa para o lado direito: 48,097 + 0,66 × 8,719.
- R1a/R1b: consumo estimado de 25,187 kg ± 30%.
- R3–R5: exigência de PM = 2.742,94 g; limite superior = 1,5 × exigência. A PM endógena do RuFaS (0,4 × 11,8 g por kg de MS) é proporcional ao consumo e por isso entra nos coeficientes, não no lado direito.
- R6, R7: Ca = 68,783 g e P = 65,517 g (o maior entre `P_req` e `P_req_process`).

## 7. Hipóteses e linearizações

O otimizador do RuFaS é **não linear** (SLSQP). Para virar um PL resolvível pelo Simplex:
1. **Restrições em % da MS reescritas na forma linear:** por exemplo, FDN ≥ 25% vira Σ(FDNᵢ − 25)·xᵢ ≥ 0. O consumo de MS pode variar na mesma faixa do RuFaS (±30%, R1a/R1b); as digestibilidades que dependem do consumo foram calculadas no consumo estimado (25,187 kg).
2. **Ponto de referência = ração do caso base** (simulação de 60 dias). Os termos que dependem da dieta inteira foram calculados nesse ponto e tratados como constantes:
   - desconto de NDT por nível de consumo = 0,8806;
   - amido total da dieta (entra na digestibilidade da FDN) = 6,956 kg;
   - concentrado na dieta (entra na taxa de passagem da proteína) = 47,42%.
3. **PM com mínimo de dois termos:** a proteína microbiana do RuFaS é min(limite por NDT, limite por PDR). Exigir PM ≥ exigência com o mínimo equivale a exigir as duas restrições lineares R3 **e** R4. Para o limite superior (R5) foi usado o termo limitado pelo NDT, o que é uma condição suficiente.
4. **Exigências fixas** da vaca média: média das duas formulações do caso base (dias 1 e 46). Perdas de metano e N urinário também vêm do caso base.
5. **Observação sobre o RuFaS:** `calculate_NASEM_dNDF` usa `(total_starch − 26)`; a equação NASEM espera o amido em % da MS, mas o RuFaS passa em kg. O modelo reproduz o cálculo do RuFaS para que a solução seja coerente com o simulador.

## 8. Verificação

- O modelo é **viável** (resolvido com HiGHS via `scipy.optimize.linprog`).
- Na solução do PL, recalculando os termos não lineares com as funções do RuFaS, a energia líquida fica -0,30% e a PM 0,01% em relação ao valor do PL (erro da linearização).
