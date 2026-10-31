#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Avaliação do efeito econômico da dieta - lote lac_cow
IFG - Pós-Graduação - Modelagem e Otimização Aplicada - Fazenda GO_campo_dourado

Compara, por vaca em lactação e por dia, o custo da ração aplicada pelo RuFaS, a produção de leite,
a receita do leite e a margem sobre o custo alimentar (receita do leite − custo da alimentação)
entre os cenários simulados:
- caso base   : ração original da fazenda (feed_caso_base.json);
- dieta do PL : dieta de custo mínimo do programa linear (feed.json);
- modo livre  : otimizador do RuFaS com ration.user_input = false (feed_modo_livre.json);
- sens_sudao  : preço da silagem de capim-sudão (176) 20% menor e dieta do PL desse cenário (feed_sens_sudao.json).
Cenários ainda não simulados são ignorados. Os cenários e seus arquivos são criados por 'preparar_cenarios.py'.

Os preços dos alimentos (R$/kg MS) e do leite (R$/kg) vêm de 'Scripts/ingredientes_racoes_GO_campo_dourado.xlsx';
o preço do leite é o do alimento 202 (leite integral, preço ao produtor em Goiás, CEPEA). No cenário sens_sudao,
o custo da ração usa o preço reduzido da silagem de capim-sudão.

Execução (a partir da raiz do RuFaS, com o ambiente virtual ativo):
    python Scripts/avaliacao_economica.py
"""

import glob
import os

import pandas as pd

from gerar_modelo_pl import BASE_DIR, FEED_NAMES_PT, PEN, load_costs
from preparar_cenarios import SUDAN_GRASS_ID, SUDAN_GRASS_PRICE_FACTOR

RATION = f'AnimalModuleReporter.report_ration_per_animal.ration_per_animal_for_{PEN}.'
MILK_COL = 'AnimalModuleReporter.report_herd_statistics_data.daily_milk_production (kg/day)'
N_COWS_COL = 'AnimalModuleReporter.report_daily_animal_population.num_lactating_cows (animals)'
CH4_COL = f'AnimalModuleReporter.report_enteric_methane_emission.enteric_methane_emission_for_{PEN} (g)'
MILK_FEED_ID = 202

# Cenário: (prefixo do CSV de saída, fatores sobre o preço de alimentos)
SCENARIOS = {
    'Caso base': ('GO_campo_dourado_caso_base_saved_variables_csv_all_variables', {}),
    'Dieta do PL': ('GO_campo_dourado_saved_variables_csv_all_variables', {}),
    'Modo livre do RuFaS': ('GO_campo_dourado_modo_livre_saved_variables_csv_all_variables', {}),
    'Capim-sudão −20%': ('GO_campo_dourado_sens_sudao_saved_variables_csv_all_variables',
                         {SUDAN_GRASS_ID: SUDAN_GRASS_PRICE_FACTOR}),
}


def latest_csv(prefix: str) -> str | None:
    csvs = sorted(glob.glob(os.path.join(BASE_DIR, 'output', 'CSVs', f'{prefix}*.csv')), key=os.path.getmtime)
    return csvs[-1] if csvs else None


def evaluate(csv_path: str, costs: dict, milk_price: float) -> dict:
    """Médias por vaca em lactação e por dia de uma simulação de 1 ano."""
    df = pd.read_csv(csv_path, low_memory=False,
                     usecols=lambda col: col.startswith(RATION) or col in (MILK_COL, N_COWS_COL, CH4_COL))
    df = df.apply(pd.to_numeric, errors='coerce')
    ration = {}
    for col in df.columns:
        key = col[len(RATION):].split(' ')[0] if col.startswith(RATION) else ''
        if key.isdigit():
            ration[int(key)] = float(df[col].dropna().mean())
    missing = [fid for fid in ration if fid not in costs]
    priced_cost = sum(kg * costs[fid][0] for fid, kg in ration.items() if fid in costs)
    cost = None if missing else priced_cost
    daily = df[[MILK_COL, N_COWS_COL, CH4_COL]].dropna()
    milk = float((daily[MILK_COL] / daily[N_COWS_COL]).mean())
    revenue = milk * milk_price
    return {
        'csv': os.path.basename(csv_path),
        'ration': ration,
        'dmi': sum(ration.values()),
        'missing': missing,
        'cost': cost,
        'priced_cost': priced_cost,
        'milk': milk,
        'ch4': float((daily[CH4_COL] / daily[N_COWS_COL]).mean()),
        'cows': float(daily[N_COWS_COL].mean()),
        'revenue': revenue,
        'iofc': None if cost is None else revenue - cost,
        'cost_per_kg_milk': None if cost is None else cost / milk,
    }


def main():
    sheet_costs = load_costs()
    milk_price = sheet_costs[MILK_FEED_ID][1] / 1000  # R$/t de matéria natural -> R$/kg de leite
    print(f'Preço do leite: R$ {milk_price:.4f}/kg\n')

    results = {}
    for name, (prefix, price_factors) in SCENARIOS.items():
        costs = {fid: (cost * price_factors.get(fid, 1.0), ton) for fid, (cost, ton) in sheet_costs.items()}
        csv_path = latest_csv(prefix)
        if csv_path is None:
            print(f'{name}: CSV não encontrado (prefixo {prefix}); cenário ainda não simulado.\n')
            continue
        r = results[name] = evaluate(csv_path, costs, milk_price)
        print(f'{name}  ({r["csv"]})')
        for fid, kg in sorted(r['ration'].items()):
            price = f'R$ {kg * costs[fid][0]:6.2f}' if fid in costs else 'sem preço'
            print(f'  {fid:<4d} {FEED_NAMES_PT.get(fid, "")[:32]:32s} {kg:7.3f} kg MS  {price}')
        print(f'  Consumo de MS         {r["dmi"]:8.2f} kg')
        print(f'  Leite                 {r["milk"]:8.2f} kg')
        print(f'  Metano entérico       {r["ch4"]:8.1f} g')
        print(f'  Vacas em lactação     {r["cows"]:8.1f} (média)')
        print(f'  Receita do leite      R$ {r["revenue"]:6.2f}')
        if r['cost'] is None:
            print(f'  Custo da ração: não calculado; alimentos sem preço: {r["missing"]}')
            print(f'  Custo só dos alimentos com preço (limite inferior) R$ {r["priced_cost"]:6.2f}\n')
            continue
        print(f'  Custo da ração        R$ {r["cost"]:6.2f}')
        print(f'  Custo por kg de leite R$ {r["cost_per_kg_milk"]:6.4f}')
        print(f'  Margem sobre o custo alimentar R$ {r["iofc"]:6.2f}/vaca/dia; '
              f'R$ {r["iofc"] * r["cows"] * 365:,.0f}/ano no rebanho\n')

    if 'Dieta do PL' in results and 'Modo livre do RuFaS' in results:
        pl, livre = results['Dieta do PL'], results['Modo livre do RuFaS']
        print('Dieta do PL − modo livre do RuFaS (por vaca por dia):')
        print(f'  Custo da ração  R$ {pl["cost"] - livre["cost"]:+.2f}')
        print(f'  Leite           {pl["milk"] - livre["milk"]:+.2f} kg')
        print(f'  Margem          R$ {pl["iofc"] - livre["iofc"]:+.2f}')


if __name__ == '__main__':
    main()
