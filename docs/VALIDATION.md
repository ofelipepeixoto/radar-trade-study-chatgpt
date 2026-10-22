# Evidência de validação — 22/10/2026

## Implementação própria

Ambiente local: Python 3.12.14, Linux. Sem instalação de dependências runtime, uso de rede, corretora ou API de LLM. Comandos executados a partir da raiz:

| Comando | Resultado observado |
| --- | --- |
| `PYTHONPATH=src python -m unittest discover -s tests -v` | 24 testes, OK, exit 0 |
| `python -m compileall -q src tests` | exit 0 |
| `python scripts/check_offline.py` | 4 arquivos de fonte, exit 0 |
| `python scripts/verify_rational.py` | 981 cenários comparados com Fraction e 3 timezones equivalentes, exit 0 |
| `PYTHONPATH=src python -m radar_trade_study examples/scenario-long.json` | JSON `status=ok`, exit 0 |

O pacote usa layout `src`: sem instalação ou `PYTHONPATH=src`, os imports não são encontrados. Uma primeira invocação local sem esse prefixo falhou por configuração; a invocação documentada acima foi então executada com sucesso. No PowerShell, configure `$env:PYTHONPATH = "src"` antes de chamar Python.

Os 24 testes cobrem direção long/short, orçamento monetário, teto de nocional, custos de ida/volta, reserva de caixa na entrada LONG, multiplicador, lote fracionário, extremos decimais, hash canônico, ausência de mutação da entrada, dados vencidos/futuros, timezone, campos faltantes/desconhecidos, booleanos, números não finitos, JSON duplicado, UTF-8 inválido, tamanho de arquivo e códigos de saída.

Revisão independente repetiu os 24 testes e examinou código/contrato. O verificador racional, com seed 94317 e `fractions.Fraction`, comparou exatamente quantidade, perda e ganho em 981 cenários de long/short, custos, lotes, multiplicadores e extremos de precisão. Conferiu ainda limites de orçamento, nocional e caixa LONG e três timezones equivalentes. O script foi preservado em `scripts/verify_rational.py` e incluído na CI. Não é auditoria certificada, teste de adequação financeira ou prova de retorno.

## Reprodução do exemplo fictício

Hash da entrada: `66232dcd4c4b322602a641be363d635f617f2d61140fbb3c9992a454f2d5a8fa`.

| Saída | Valor |
| --- | --- |
| quantity | 9 |
| notional | USD 900 |
| modeled_loss | USD 91,98 |
| net_gain | USD 178,02 |
| roundtrip_cost | USD 1,98 |
| entry_cost | USD 0,90 |
| entry_outlay | USD 900,90 |
| cash_remaining | USD 9.099,10 |
| risk_reward_ratio | 1,935420743639, truncado a 12 casas |

Aritmética independente: entrada 100, stop 90, alvo 120; `fee=5` e `slippage=5`, total **10 bps por lado**. Custo conservador por unidade = `(100+120) × 10/10000 = 0,22`, perda por unidade **10,22** e ganho líquido **19,78**. A quantidade inteira é `floor(min(100/10,22; 1000/100; 10000/100,10)) = 9`. Custo total **1,98**; entrada **0,10 × 9 = 0,90**. A taxa de entrada está incluída nos custos de ida/volta e não é somada novamente à perda modelada.

## Limites da verificação

Execução local realizada em Python 3.12.14. A [CI da implementação](https://github.com/ofelipepeixoto/radar-trade-study-chatgpt/actions/runs/39722831355), sobre `bae4838b5cecaac2ae5e7cbacecd21a8a9ec6512`, passou nos dois jobs: Python 3.11 e 3.12. Windows/PowerShell não foi exercitado. Não se executou instalação de wheel, load test, teste de usuário em uma nova conversa ChatGPT, coleta de mercado, integração MCP, deploy ou transação. O motor foi executado por ferramenta de código; isso não comprova que todos os ambientes ChatGPT terão Python ou lerão todos os arquivos.

CI é configurada com permissões de leitura e Actions fixadas por SHA consultado no GitHub. As [execuções posteriores](https://github.com/ofelipepeixoto/radar-trade-study-chatgpt/actions/workflows/checks.yml) devem ser verificadas por revisão; configuração não equivale a execução concluída.

## Integração em main

Em 22/10/2026, a auditoria foi integrada pela [PR #1](https://github.com/ofelipepeixoto/radar-trade-study-chatgpt/pull/1), merge `b0499df069e12a7066bfa11aaa61b555b8bd76ba`, e a implementação pela [PR #2](https://github.com/ofelipepeixoto/radar-trade-study-chatgpt/pull/2), merge `57010b780fd0a00d0edbbb1065ebd3d195cd40af`. A árvore de `main` passou a conter 30 arquivos versionados, incluindo instruções, guia, contrato, motor, exemplo, testes, CI e relatório.

Os 29 arquivos de texto dessa revisão foram obtidos do GitHub e conferidos por seus hashes de blob. Nessa cópia da revisão combinada, os 24 testes passaram novamente; o verificador racional confirmou 981 cenários e três timezones, a checagem offline conferiu quatro arquivos de runtime e a CLI executou o exemplo fictício com os mesmos números e hash de entrada registrados acima. A [CI após o merge](https://github.com/ofelipepeixoto/radar-trade-study-chatgpt/actions/runs/39724532692) também concluiu com sucesso sobre essa revisão de `main`. A imagem de criação em `docs/audit/repository-created.png` é registro histórico do bootstrap, anterior à integração.

## Upstream

A [auditoria](audit/2026-10-22-day-trader-skill.md) e o [método de validação upstream](audit/UPSTREAM-VALIDATION.md) estão em `main`. Foram observados 315 testes upstream passando e três regressões adicionais reproduzidas, sem reutilizar código upstream no runtime próprio. Essas reproduções não foram repetidas na integração documental; a validação nova descrita acima cobre a implementação própria combinada.
