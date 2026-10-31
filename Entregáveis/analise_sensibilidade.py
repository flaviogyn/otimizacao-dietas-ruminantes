#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise de sensibilidade do programa linear de custo mínimo - lote lac_cow
IFG - Pós-Graduação - Modelagem e Otimização Aplicada - Fazenda GO_campo_dourado

Usa o mesmo modelo de 'gerar_modelo_pl.py' (coeficientes, restrições e solver PuLP/CBC) e calcula:
1. Preços-sombra das restrições e custos reduzidos dos alimentos na solução ótima.
2. Faixas de validade dos custos: quanto o preço de cada alimento pode variar sem mudar a base ótima
   (mesmos alimentos na dieta e mesmas restrições ativas).
3. Faixas de validade das exigências (MS, energia, PM, Ca, P): quanto cada uma pode variar sem mudar a base,
   intervalo em que o preço-sombra correspondente continua válido.
4. Cenários paramétricos de preços e de exigências, re-resolvendo o modelo em cada caso.

As faixas são obtidas re-resolvendo o modelo e localizando, por bisseção, o ponto em que a base muda.

Execução (a partir da raiz do RuFaS, com o ambiente virtual ativo):
    python Scripts/analise_sensibilidade.py
"""

import copy

import pulp

from gerar_modelo_pl import (
    FEED_NAMES_PT,
    REQ,
    build_coefficients,
    build_constraints,
    build_pulp_model,
    load_costs,
    load_feed_library,
    reference_point,
)

TOL = 1e-7          # tolerância para considerar um alimento na dieta ou uma restrição ativa
BISECTION_TOL = 1e-4  # precisão relativa das faixas
MAX_FACTOR = 10.0   # busca até 10 vezes o valor original (acima disso, a faixa é dada como ilimitada)

# Exigências e as restrições em que cada uma aparece no lado direito.
REQUIREMENTS = {
    'Consumo de MS (kg)': ['R1a_consumo_MS_min', 'R1b_consumo_MS_max'],
    'Energia líquida (Mcal)': ['R2_energia_liquida'],
    'Proteína metabolizável (g)': ['R3_PM_min_NDT', 'R4_PM_min_PDR', 'R5_PM_max'],
    'Cálcio (g)': ['R6_calcio'],
    'Fósforo (g)': ['R7_fosforo'],
}


def solve(c, cons) -> dict:
    """Resolve o PL e devolve custo, dieta, duais, custos reduzidos e a base (alimentos e restrições ativas)."""
    prob, xv = build_pulp_model(c, cons)
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    if pulp.LpStatus[prob.status] != 'Optimal':
        return {'ok': False}
    x = {fid: xv[fid].value() or 0.0 for fid in c.index}
    active = tuple(k['nome'] for k in cons
                   if abs(prob.constraints[k['nome']].slack) < 1e-6 * max(1.0, abs(k['rhs'])))
    return {
        'ok': True,
        'z': pulp.value(prob.objective),
        'x': x,
        'duals': {k['nome']: prob.constraints[k['nome']].pi for k in cons},
        'reduced': {fid: xv[fid].dj for fid in c.index},
        'basis': (tuple(fid for fid, v in x.items() if v > TOL), active),
    }


def with_cost(c, fid, value):
    c2 = c.copy()
    c2.at[fid, 'custo'] = value
    return c2


def with_rhs(cons, names, factor):
    cons2 = copy.deepcopy(cons)
    for k in cons2:
        if k['nome'] in names:
            k['rhs'] *= factor
    return cons2


def find_limit(same_basis, start: float, end: float) -> float | None:
    """Último valor entre start e end com a mesma base; None se a base não muda até end."""
    if same_basis(end):
        return None
    lo, hi = start, end
    while abs(hi - lo) > BISECTION_TOL * max(abs(start), 1e-6):
        mid = (lo + hi) / 2
        if same_basis(mid):
            lo = mid
        else:
            hi = mid
    return lo


def cost_ranges(c, cons, base) -> list[dict]:
    rows = []
    for fid in c.index:
        cost = c.at[fid, 'custo']

        def same_basis(value, fid=fid):
            s = solve(with_cost(c, fid, value), cons)
            return s['ok'] and s['basis'] == base['basis']

        lower = find_limit(same_basis, cost, 0.0)
        upper = find_limit(same_basis, cost, cost * MAX_FACTOR)
        rows.append({'feed': fid, 'custo': cost, 'x': base['x'][fid],
                     'min': 0.0 if lower is None else lower, 'max': upper})
    return rows


def rhs_ranges(c, cons, base) -> list[dict]:
    rows = []
    for name, cons_names in REQUIREMENTS.items():

        def same_basis(factor, cons_names=cons_names):
            s = solve(c, with_rhs(cons, cons_names, factor))
            return s['ok'] and s['basis'] == base['basis']

        # Consumo de MS: mostra o consumo estimado, do qual derivam os limites R1a e R1b.
        rhs = REQ['DMI'] if name.startswith('Consumo') else next(k['rhs'] for k in cons if k['nome'] == cons_names[0])
        lower = find_limit(same_basis, 1.0, 0.0)
        upper = find_limit(same_basis, 1.0, MAX_FACTOR)
        rows.append({'exigencia': name, 'rhs': rhs,
                     'dual': sum(base['duals'][n] for n in cons_names),
                     'min': 0.0 if lower is None else lower, 'max': upper})
    return rows


def scenarios(c, cons) -> list[tuple[str, object, list]]:
    """Cenários paramétricos: (descrição, coeficientes, restrições)."""
    out = [('Solução de referência', c, cons)]
    for fid, pcts in ((51, (-20, +20)), (303, (-20, +20)), (301, (+20,)), (44, (-20,)), (176, (-20,))):
        for p in pcts:
            out.append((f'Preço do alimento {fid} {p:+d}%',
                        with_cost(c, fid, c.at[fid, 'custo'] * (1 + p / 100)), cons))
    nutrients = [n for name, names in REQUIREMENTS.items() if name != 'Consumo de MS (kg)' for n in names]
    for p in (-10, +10):
        out.append((f'Exigências de energia, PM, Ca e P {p:+d}%', c, with_rhs(cons, nutrients, 1 + p / 100)))
    out.append(('Margem de segurança de cálcio (×1,02)', c, with_rhs(cons, ['R6_calcio'], 1.02)))
    return out


def br(v: float, nd: int = 4) -> str:
    return f'{v:,.{nd}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def main():
    lib = load_feed_library()
    c = build_coefficients(lib, load_costs(), reference_point(lib))
    cons, _ = build_constraints(c)
    base = solve(c, cons)
    print(f'Custo ótimo: R$ {br(base["z"])}/vaca/dia')
    print(f'Alimentos na dieta: {base["basis"][0]}; restrições ativas: {base["basis"][1]}\n')

    print('1. Preços-sombra das restrições ativas (R$ por unidade do lado direito)')
    for name in base['basis'][1]:
        print(f'  {name:22s} {br(base["duals"][name])}')
    print('\n   Custos reduzidos dos alimentos fora da dieta (R$/kg MS)')
    for fid in sorted((f for f in c.index if base['x'][f] <= TOL), key=lambda f: base['reduced'][f]):
        print(f'  {fid:<4d} {FEED_NAMES_PT[fid]:38s} {br(base["reduced"][fid])}')

    print('\n2. Faixas de custo com a mesma base (R$/kg MS)')
    print(f'  {"id":<4s} {"alimento":38s} {"atual":>8s} {"mínimo":>8s} {"máximo":>8s} {"queda":>8s} {"alta":>9s}')
    for r in cost_ranges(c, cons, base):
        up = '∞' if r['max'] is None else br(r['max'])
        up_pct = '∞' if r['max'] is None else f'{(r["max"] / r["custo"] - 1) * 100:+.1f}%'
        print(f'  {r["feed"]:<4d} {FEED_NAMES_PT[r["feed"]]:38s} {br(r["custo"]):>8s} {br(r["min"]):>8s} {up:>8s} '
              f'{(r["min"] / r["custo"] - 1) * 100:+7.1f}% {up_pct:>9s}')

    print('\n3. Faixas das exigências com a mesma base (preço-sombra válido)')
    print(f'  {"exigência":28s} {"atual":>10s} {"preço-sombra":>13s} {"mínimo":>10s} {"máximo":>10s} {"variação":>16s}')
    for r in rhs_ranges(c, cons, base):
        # Sem mudança de base até o limite da busca: a faixa vai além de MAX_FACTOR vezes o valor atual.
        up = f'> {MAX_FACTOR:g}×' if r['max'] is None else br(r['rhs'] * r['max'], 2)
        up_pct = f'> {MAX_FACTOR:g}×' if r['max'] is None else f'{(r["max"] - 1) * 100:+.1f}%'
        print(f'  {r["exigencia"]:28s} {br(r["rhs"], 2):>10s} {br(r["dual"]):>13s} {br(r["rhs"] * r["min"], 2):>10s} '
              f'{up:>10s} {(r["min"] - 1) * 100:+6.1f}% a {up_pct}')

    print('\n4. Cenários paramétricos')
    feeds = [fid for fid in c.index]
    for desc, c_s, cons_s in scenarios(c, cons):
        s = solve(c_s, cons_s)
        if not s['ok']:
            print(f'  {desc}: sem solução viável')
            continue
        diet = ', '.join(f'{fid}: {br(s["x"][fid], 3)}' for fid in feeds if s['x'][fid] > TOL)
        same = 'mesma base' if s['basis'] == base['basis'] else 'base muda'
        print(f'  {desc:52s} Z = R$ {br(s["z"], 2)} ({(s["z"] / base["z"] - 1) * 100:+.1f}%), {same}; '
              f'MS {br(sum(s["x"].values()), 2)} kg -> {diet}')


if __name__ == '__main__':
    main()
