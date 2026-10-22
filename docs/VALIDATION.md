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

Python 3.11 está previsto na matriz CI; execução local realizada em 3.12. Windows/PowerShell não foi exercitado. Não se executou instalação de wheel, load test, teste de usuário em uma nova conversa ChatGPT, coleta de mercado, integração MCP, deploy ou transação. O motor foi executado por ferramenta de código nesta sessão; isso não comprova que todos os ambientes ChatGPT terão Python ou lerão todos os arquivos.

CI é configurada com permissões de leitura e Actions fixadas por SHA consultado no GitHub. O resultado hospedado deve ser consultado na PR; configuração não equivale a execução concluída. A branch `main` permanece no bootstrap até revisão e merge autorizados.

## Upstream

Auditoria e suíte upstream são propostas em PR independente. Foram observados 315 testes upstream passando e três regressões adicionais reproduzidas, sem reutilizar código upstream no runtime próprio. Consulte os documentos da PR de auditoria para revisão, método e reprodução.
