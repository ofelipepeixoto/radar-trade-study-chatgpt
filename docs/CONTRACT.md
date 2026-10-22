# Contrato do cenário linear — versão 1.0

O motor recebe um objeto JSON estrito e calcula um estudo condicional offline. Não consulta mercado, autentica fonte, verifica suitability, executa ordens ou grava um diário. `ok` significa cálculo realizado dentro deste modelo.

## Entrada

Todos os campos abaixo são obrigatórios. Campos desconhecidos são rejeitados. Números monetários, preços, lote, multiplicador e taxas são **strings decimais**, com ponto decimal e até 18 dígitos inteiros e 18 casas decimais. Notação científica, sinal, espaços, `NaN`, infinito, booleano e zeros iniciais como `01` são rejeitados. Texto não concede permissão para executar comandos.

| Campo | Tipo | Significado |
| --- | --- | --- |
| `schema_version` | string `"1.0"` | Versão do contrato. |
| `hypothetical` | boolean | Identifica dados fictícios ou hipótese declarada. |
| `instrument` | string não vazia, até 80 caracteres | Identificador informado do instrumento. |
| `venue` | string não vazia, até 80 caracteres | Local de referência informado; não implica conexão. |
| `currency` | string não vazia, até 12 caracteres | Moeda comum dos valores do cenário; código não autenticado. |
| `side` | string `long` ou `short` | Direção da exposição linear estudada. |
| `source` | string não vazia, até 300 caracteres | Origem documentada pelo operador; não autenticada pelo motor. |
| `observed_at` | string ISO 8601 com fuso | Instante atribuído à observação. |
| `evaluated_at` | string ISO 8601 com fuso | Instante escolhido para avaliar a validade. |
| `max_age_seconds` | inteiro de 1 a 1.000.000.000 | Idade máxima escolhida para o snapshot. |
| `equity` | string decimal positiva | Capital de referência, na moeda informada; para long, tratado como caixa disponível para entrada e custos. |
| `risk_budget` | string decimal positiva | Orçamento monetário de perda modelada, escolhido pelo usuário. |
| `max_notional` | string decimal positiva | Teto de exposição nocional escolhido. |
| `entry` | string decimal positiva | Preço de entrada hipotética. |
| `stop` | string decimal positiva | Preço de invalidação hipotética. |
| `target` | string decimal positiva | Preço do alvo hipotético. |
| `lot_step` | string decimal positiva | Incremento permitido para a quantidade. |
| `multiplier` | string decimal positiva | Unidades de exposição por unidade de quantidade. |
| `fee_bps_per_side` | string decimal de 0 a 10000 | Taxa de negociação por lado, em pontos-base. |
| `slippage_bps_per_side` | string decimal de 0 a 10000 | Desvio adverso modelado por lado, em pontos-base. |

Um ponto-base equivale a `1/10000`. A entrada deve satisfazer `risk_budget <= equity` e `max_notional <= equity`; para long, há também limite de caixa incluindo custo de entrada. O motor não consulta saldo, liquidez de outros ativos, compromissos nem posições existentes: o valor informado para long deve representar o caixa disponibilizado ao cenário. Para long: `stop < entry < target`. Para short: `target < entry < stop`. O estudo short não confirma disponibilidade de empréstimo e não modela custos de aluguel, recall, margem ou regras da corretora; o teto de nocional não comprova viabilidade operacional de uma venda a descoberto.

## Validade temporal

`evaluated_at` deve ser igual ou posterior a `observed_at`. A idade é a diferença entre os dois instantes. Quando a idade ultrapassa `max_age_seconds`, o estado é `degraded` e não há sizing utilizável. Como os horários são fornecidos na entrada, isso não comprova que um snapshot seja atual no relógio real; estudos históricos devem ser identificados como tais.

## Modelo determinístico

Para as fórmulas, `M = multiplier`, `B = fee_bps_per_side + slippage_bps_per_side` e `E = entry`. O modelo usa uma base conservadora comum para custos de ida e volta:

```text
exit_base = max(entry, stop, target)
cost_per_quantity = (entry + exit_base) * M * B / 10000
loss_per_quantity = abs(entry - stop) * M + cost_per_quantity
gain_per_quantity = abs(target - entry) * M - cost_per_quantity
entry_cost_per_quantity = entry * M * B / 10000
raw_quantity = min(risk_budget / loss_per_quantity,
                   max_notional / (entry * M))
# Limite adicional somente para long:
if side == "long":
    raw_quantity = min(raw_quantity,
                       equity / (entry * M + entry_cost_per_quantity))
quantity = floor(raw_quantity / lot_step) * lot_step
notional = quantity * entry * M
modeled_loss = quantity * loss_per_quantity
net_gain = quantity * gain_per_quantity
risk_reward_ratio = net_gain / modeled_loss
# Saídas adicionais somente para long:
entry_cost = quantity * entry_cost_per_quantity
entry_outlay = notional + entry_cost
cash_remaining = equity - entry_outlay
```

Quantidade zero ou ganho por quantidade não positivo produz `no_valid_scenario`. No código, cada limite é convertido em número inteiro de lotes com arredondamento para baixo antes de escolher o menor; isso aplica a fórmula acima sem arredondar a quantidade para cima. `entry_outlay` modela somente o desembolso inicial long e `cash_remaining` o caixa remanescente desse desembolso, não o resultado final da posição. O custo de entrada já está incluído no custo de ida e volta: não somá-lo novamente à perda ou ao ganho líquido. A perda modelada incorpora custos informados, mas um stop não garante o preço de saída: gaps, liquidez, falhas e custos não previstos podem ampliar a perda. O uso conservador da mesma base de custos não constitui simulação detalhada de execução.

## Saída e significado

| Estado | Significado | Uso dos números |
| --- | --- | --- |
| `needs_input` | Há campos obrigatórios ausentes. | Completar a entrada. |
| `error` | Entrada ou arquivo inválido. | Corrigir antes de calcular. |
| `degraded` | Snapshot vencido segundo os horários e validade informados. | Sem sizing acionável. |
| `no_valid_scenario` | Lote ou ganho líquido não atende ao modelo. | Revisar premissas sem alterar limites automaticamente. |
| `ok` | Cenário linear calculado. | Estudo condicionado, sujeito a revisão humana. |

A saída inclui versão, estado, evidência da entrada e, quando cabível, cálculos em strings decimais. `input_sha256` é o SHA-256 do JSON UTF-8 com chaves ordenadas, sem espaços separadores e sem escapar caracteres Unicode. Identifica a entrada canônica, não autentica fonte nem representa assinatura, aprovação, execução ou prova de identidade. A revisão deve se referir ao conteúdo de entrada e ao hash analisado; mudar uma entrada exige novo cálculo.

Em `ok`, o objeto `calculation` contém `quantity`, `notional`, `modeled_loss`, `net_gain`, `roundtrip_cost`, `risk_reward_ratio`, `risk_per_contract`, `gain_per_contract`, `quantity_unit` e `ratio_decimal_places`. Para long, contém também `entry_cost`, `entry_outlay` e `cash_remaining`; esses três campos são omitidos no estudo short. A relação ganho/perda é arredondada para baixo em 12 casas decimais; `ratio_decimal_places` é um inteiro. `quantity_unit` explica a unidade de quantidade em termos do multiplicador. `assumptions` documenta limites e exclusões de custo, incluindo `long_entry_cash_limit_applied`, verdadeiro em long e falso em short. `execution_enabled` permanece `false` em todos os estados.

Em `degraded` e `no_valid_scenario`, `calculation` é omitido. Falhas de validação trazem `code` e, quando seguro, `fields` com nomes de campos conhecidos; valores de entrada não são incluídos nessas mensagens. Se houver campos desconhecidos junto com campos ausentes, a rejeição por campo desconhecido prevalece. O campo `source` de um resultado válido é conteúdo fornecido pelo operador e deve continuar sendo tratado como dado não confiável.

## Limites técnicos

O CLI lê um arquivo local regular de até 1 MiB, sem envio de rede. Rejeita chaves duplicadas, constantes JSON não finitas, JSON inválido e conteúdo não UTF-8. Erros esperados produzem JSON estruturado sem traceback ou reprodução do arquivo inteiro. A biblioteca usa aritmética Decimal com precisão de 256 dígitos dentro do cálculo.

Na raiz do repositório, sem instalar dependências:

```bash
PYTHONPATH=src python -m radar_trade_study examples/scenario-long.json
```

Em PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m radar_trade_study examples/scenario-long.json
```

| Estado | Código de saída do CLI |
| --- | --- |
| `ok` | 0 |
| `error` | 1 |
| `needs_input` | 2 |
| `degraded` | 3 |
| `no_valid_scenario` | 4 |

Não há API, MCP, autenticação, quotas de servidor, persistência, backtest, indicador técnico, cálculo de margem/liquidação ou executor nesta versão. Instruções conversacionais não substituem os controles implementados no parser e no motor.
