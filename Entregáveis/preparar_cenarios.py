#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preparação dos cenários adicionais de simulação do RuFaS - fazenda GO_campo_dourado
IFG - Pós-Graduação - Modelagem e Otimização Aplicada

Cria, a partir dos arquivos da simulação com a dieta do PL, os arquivos de entrada de dois cenários:
- modo_livre : otimizador do RuFaS com ration.user_input = false; a ração das vacas em lactação lista os
               9 alimentos candidatos do PL (em modo livre o RuFaS usa só a lista, não os percentuais).
- sens_sudao : preço da silagem de capim-sudão (176) 20% menor e a ração das vacas em lactação trocada pela
               solução do PL nesse cenário (análise de sensibilidade).

Para cada cenário são gravados, em GO_campo_dourado/: feed_<cenario>.json (e animal_<cenario>.json, quando
muda), farm_metadata_<cenario>.json, _pipeline_tasks_<cenario>.json e
_pipeline_task_manager_metadata_<cenario>.json. Mesmo período (1 ano) e semente (44) das demais simulações.

Execução (a partir da raiz do RuFaS, com o ambiente virtual ativo):
    python Scripts/preparar_cenarios.py
    python main.py -p GO_campo_dourado/_pipeline_task_manager_metadata_modo_livre.json -g
    python main.py -p GO_campo_dourado/_pipeline_task_manager_metadata_sens_sudao.json -g
"""

import json
import os

from analise_sensibilidade import solve, with_cost
from gerar_modelo_pl import (
    BASE_DIR,
    FEEDS,
    build_coefficients,
    build_constraints,
    load_costs,
    load_feed_library,
    reference_point,
)

FARM_DIR = os.path.join(BASE_DIR, 'GO_campo_dourado')
INPUTS_DIR = os.path.join(FARM_DIR, 'inputs_resolvidos')
SUDAN_GRASS_ID = 176
SUDAN_GRASS_PRICE_FACTOR = 0.8


def load(path):
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def save(data, path):
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    print(f'  {os.path.relpath(path, BASE_DIR)}')


def set_lac_cow_ration(feed_cfg: dict, percentages: dict[int, float]) -> None:
    for ration in feed_cfg['rations']:
        if ration['animal_combination'] == 'lac_cow':
            ration['feeds'] = [{'feed_type': fid, 'ration_percentage': p} for fid, p in percentages.items()]


def write_scenario(name: str, feed_cfg: dict, animal_cfg: dict | None = None) -> None:
    rel = 'GO_campo_dourado'
    save(feed_cfg, os.path.join(INPUTS_DIR, f'feed_{name}.json'))
    metadata = load(os.path.join(FARM_DIR, 'farm_metadata.json'))
    metadata['files']['feed']['path'] = f'{rel}/inputs_resolvidos/feed_{name}.json'
    if animal_cfg is not None:
        save(animal_cfg, os.path.join(INPUTS_DIR, f'animal_{name}.json'))
        metadata['files']['animal']['path'] = f'{rel}/inputs_resolvidos/animal_{name}.json'
    save(metadata, os.path.join(FARM_DIR, f'farm_metadata_{name}.json'))

    tasks = load(os.path.join(FARM_DIR, '_pipeline_tasks.json'))
    tasks['tasks'][0]['metadata_file_path'] = f'{rel}/farm_metadata_{name}.json'
    tasks['tasks'][0]['output_prefix'] = f'GO_campo_dourado_{name}'
    save(tasks, os.path.join(FARM_DIR, f'_pipeline_tasks_{name}.json'))

    manager = load(os.path.join(FARM_DIR, '_pipeline_task_manager_metadata.json'))
    manager['files']['tasks']['path'] = f'{rel}/_pipeline_tasks_{name}.json'
    save(manager, os.path.join(FARM_DIR, f'_pipeline_task_manager_metadata_{name}.json'))


def main():
    feed_cfg = load(os.path.join(INPUTS_DIR, 'feed.json'))

    print('Cenário modo_livre:')
    free = json.loads(json.dumps(feed_cfg))
    shares = [100 - 11 * (len(FEEDS) - 1)] + [11] * (len(FEEDS) - 1)  # percentuais ignorados em modo livre
    set_lac_cow_ration(free, dict(zip(FEEDS, shares)))
    animal_cfg = load(os.path.join(INPUTS_DIR, 'animal.json'))
    animal_cfg['ration']['user_input'] = False
    write_scenario('modo_livre', free, animal_cfg)

    print('Cenário sens_sudao:')
    lib = load_feed_library()
    c = build_coefficients(lib, load_costs(), reference_point(lib))
    cons, _ = build_constraints(c)
    price = c.at[SUDAN_GRASS_ID, 'custo'] * SUDAN_GRASS_PRICE_FACTOR
    s = solve(with_cost(c, SUDAN_GRASS_ID, price), cons)
    total = sum(s['x'].values())
    percentages = {fid: round(v / total * 100, 1) for fid, v in s['x'].items() if v > 1e-7}
    print(f'  dieta do PL: R$ {s["z"]:.4f}/vaca/dia, {total:.3f} kg MS, % da MS: {percentages}')
    sudan = json.loads(json.dumps(feed_cfg))
    for feed in sudan['feeds']:
        if feed['feed_type'] == SUDAN_GRASS_ID:
            feed['purchased_feed_cost'] = round(price, 4)
    set_lac_cow_ration(sudan, percentages)
    write_scenario('sens_sudao', sudan)


if __name__ == '__main__':
    main()
