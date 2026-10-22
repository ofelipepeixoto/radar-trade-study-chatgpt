# Jornada e interação

Estado deste documento: especificação para a conversa no ChatGPT e para uma possível interface futura. Nenhuma interface web, autenticação, teste com usuário ou integração de mercado é comprovada por este documento.

## Objetivo e hipótese

Permitir que uma pessoa entenda um cenário linear e encontre premissas ausentes sem confundir resultado de cálculo com autorização de investimento. Hipótese a validar: um exemplo fictício e uma tabela curta de entradas reduzem dúvidas em comparação com um prompt livre longo. Ainda não houve teste de usabilidade nem medição desse efeito.

## Fluxo recomendado

1. **Escolher tarefa:** estudar o exemplo, analisar snapshot ou identificar lacunas. Não repetir a escolha se a intenção já estiver clara.
2. **Conferir entradas:** mostrar origem, horários e hipóteses antes dos números derivados. Agrupar campos por referência de mercado, limites e custos.
3. **Calcular ou explicar:** usar execução real quando disponível; declarar explicitamente a ausência de runner.
4. **Revisar estudo:** apresentar estado, valores com unidades, limitações e uma próxima ação clara. Cada mudança de entrada gera outro resultado.

Não há envio, carteira conectada, monitoramento ou sequência de aprovação financeira neste fluxo.

## Estados e recuperação

| Estado | Texto principal sugerido | Ação principal | Efeito e recuperação |
| --- | --- | --- | --- |
| `needs_input` | “Faltam estes dados para calcular.” | Completar campos listados | Retomar com os valores válidos já fornecidos. |
| `error` | “Há um valor ou formato inválido.” | Corrigir campo indicado | Mostrar requisito e exemplo; não produzir sizing parcial. |
| `degraded` | “O snapshot ultrapassou a validade informada.” | Atualizar referência ou estudar o histórico | Não apresentar quantidade acionável. |
| `no_valid_scenario` | “O cenário não cabe nos limites ou não oferece ganho líquido positivo.” | Revisar premissas | Não elevar limites automaticamente. |
| `ok` | “Cenário condicional calculado.” | Revisar entradas e limitações | Explicar que cálculo não equivale a adequação ou aprovação. |

Estados de conta, acesso negado, fila e execução remota não se aplicam ao CLI offline. Não inventar indicadores de carregamento, percentuais de progresso ou confirmação de cancelamento de um serviço inexistente.

## Especificação da etapa prioritária: revisão do estudo

**ID:** estudo-01. **Papel:** pessoa que analisa o cenário. **Entrada:** JSON validado ou erros estruturados. **Saída:** resultado compreendido e premissas a conferir.

Hierarquia: título e significado do estado; aviso “dados fictícios” quando aplicável; instrumento/moeda/fonte/horários; tabela de entradas; tabela de cálculo com unidades; lacunas e riscos; uma ação de revisão. Para long, mostrar desembolso de entrada e caixa restante junto do nocional, explicando que taxa e slippage de entrada foram reservados no limite de caixa. Não somar esse custo outra vez à perda modelada ou ao custo de ida e volta. Detalhes técnicos como hash e comando ficam após a explicação principal, mas disponíveis para conferência.

A ação principal é **Revisar premissas**. A ação secundária é **Ver evidência do cálculo**. Em uma UI futura, não oferecer “Operar”, “Aprovar trade” ou “Conectar conta”. Não usar verde para comunicar segurança de investimento. Short exige texto visível sobre empréstimo e custos não cobertos.

## Linguagem, mobile e acessibilidade

Use “orçamento de risco”, “perda modelada” e “quantidade teórica”; explique “nocional” no primeiro uso. Mostre moeda junto aos valores monetários e unidade junto à quantidade. Números longos não devem esconder a unidade nem exigir rolagem horizontal para entender o estado. Em uma futura UI, use rótulos persistentes, erros associados aos campos, foco visível e navegação completa por teclado. Estado deve ser reconhecível pelo texto, sem depender de cor.

O histórico da conversa permite consultar respostas anteriores conforme os recursos do ChatGPT. O projeto não implementa banco, salvamento de rascunho nem retomada garantida. Não mostrar “salvo” ou “desfazer” sem mecanismo correspondente.

## Critérios de aceite e validação futura

- A pessoa identifica que o exemplo é fictício e que `ok` não autoriza uma operação.
- Consegue localizar fonte, horários, custos e campo que impediu o cálculo.
- Distingue perda modelada de perda máxima garantida e risco de capital alocado.
- Em long, distingue nocional de desembolso inicial e identifica que o capital informado é tratado como caixa disponível, sem verificação de saldo real.
- Reconhece se houve execução real ou somente explicação qualitativa.
- Após editar uma entrada, consegue identificar o novo resultado sem reutilizar revisão anterior.

Em teste futuro, registrar conclusão da tarefa, erros de interpretação e pedidos de ajuda, com consentimento e minimização de dados. Não há telemetria instalada nem metas quantitativas validadas nesta versão.
