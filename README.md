# otimizacao-dietas-ruminantes

Otimização de Dietas de Custo Mínimo Com Rufas &amp; Programação Linear

## links

https://docs.google.com/spreadsheets/d/1TkHq5Xkb9-thYC84IiIQxabuJ_picFvQ2Sb5rjSeV2w/edit?gid=0#gid=0
https://docs.google.com/document/d/1ZP6GWdINI7LjcmYgJNcA2FmCdW6Y-LEnpo3T8rguPJY/edit?tab=t.0

## RuFas

git@github.com:RuminantFarmSystems/RuFaS.git

## Dashboard

https://rufas-dashboard.streamlit.app/
https://github.com/leandroalexandre-ifg/rufas-filter

```bash
  ___________________________
| Good Mooooorning Professor! |
  ===========================
                 \
                  \
                    ^__^
                    (oo)\_______
                    (__)\       )\/\
                        ||----w |
                        ||     ||
```

## Estrutura Operacional

- **Simulador Oficial**: [`RuFaS-dev`](file:///d:/projetos/ia/IFG/otimizacao-dietas-ruminantes/RuFaS-dev) (ambiente Python 3.13 com `.venv` configurado).
- **Template do Caso Base**: [`Fazenda Campo Dourado`](file:///d:/projetos/ia/IFG/otimizacao-dietas-ruminantes/Fazenda%20Campo%20Dourado) (cenário `GO_campo_dourado` com rebanho, clima de GO e dados resolvidos).
- **Documentação e Relatórios**: [`docs/`](file:///d:/projetos/ia/IFG/otimizacao-dietas-ruminantes/docs) (fundamentação em programação linear, zootecnia, aulas e manuais).
- **Manual Passo a Passo**: [`GUIA_INTEGRACAO_RUFAS_DEV.md`](file:///d:/projetos/ia/IFG/otimizacao-dietas-ruminantes/GUIA_INTEGRACAO_RUFAS_DEV.md) (roteiro completo de parametrização e execução).

## Execução Rápida

Para rodar a simulação da fazenda em Goiás no `RuFaS-dev`:

```powershell
# 1. Copiar o cenário para a raiz do simulador (se ainda não estiver lá):
Copy-Item -Recurse -Path ".\Fazenda Campo Dourado\GO_campo_dourado" -Destination ".\RuFaS-dev\GO_campo_dourado"

# 2. Entrar na pasta do simulador:
cd RuFaS-dev

# 3. Disparar a simulação:
.\.venv\Scripts\python.exe main.py -p GO_campo_dourado\_pipeline_task_manager_metadata.json
# ou: uv run python main.py -p GO_campo_dourado\_pipeline_task_manager_metadata.json
```

