# Usar no ChatGPT

Este repositório contém instruções e um motor Python offline. Ele não instala uma extensão nem conecta uma corretora. O uso de arquivos e instruções em Projetos foi conferido na [documentação oficial de Projetos](https://learn.chatgpt.com/docs/projects) em 22/10/2026. A disponibilidade de execução depende do ambiente e das ferramentas da conversa.

## Preparar o projeto

1. Crie um Projeto no ChatGPT com o nome **Radar Trade Study**.
2. Copie o conteúdo de `INSTRUCOES.md` para as instruções do Projeto.
3. Adicione `docs/CONTRACT.md`, `examples/scenario-long.json` e os quatro arquivos do pacote: `src/radar_trade_study/__init__.py`, `engine.py`, `cli.py` e `__main__.py`. Preserve nomes e estrutura quando trabalhar em uma pasta acessível ao ambiente de código. Em uma conversa apenas com anexos, peça ao ChatGPT para identificar o caminho real de cada arquivo antes de executar. O arquivo `engine.py` isolado não contém a interface de execução completa. Não anexe pastas de cache `__pycache__`.
4. Comece com os dados fictícios. Não adicione extratos, identificadores de conta ou segredos para esse teste.

Adicionar o README ou um link GitHub, isoladamente, não comprova que o motor foi lido ou executado. Arquivos podem precisar ser anexados novamente quando não estiverem acessíveis na conversa. Não há sincronização automática com o repositório configurada por este pacote.

## Primeiro pedido

> Use as instruções do Radar Trade Study. Leia o contrato, o exemplo fictício e os quatro arquivos do pacote Python. Liste os arquivos lidos. Se houver Python, execute o motor no exemplo e informe comando, código de saída e resultado. Explique quantidade teórica, nocional, perda modelada, custos, desembolso inicial, caixa restante e limitações. Se não houver execução de código, declare isso e faça somente a explicação qualitativa. Não trate `ok` como aprovação de uma operação.

## Conferir o resultado

O relato deve mostrar evidência de execução real e identificar os dados como fictícios. Os horários do exemplo servem ao estudo reproduzível; não representam mercado atual. Confira o resultado contra o JSON produzido pelo motor, sem exigir números de memória.

| Situação observada | Próxima ação |
| --- | --- |
| Arquivo ausente | Adicionar somente o arquivo identificado e retomar. |
| Python indisponível | Usar a explicação qualitativa e registrar execução pendente. |
| Campo ausente ou formato inválido | Corrigir o campo; preservar as outras entradas. |
| Snapshot vencido | Obter novo snapshot com fonte e horário ou manter o caso como histórico. |
| Cenário calculado | Revisar premissas e custos; não há botão ou comando de envio de ordem. |

## Analisar um snapshot próprio

Copie o formato do exemplo e substitua os valores com fonte documentada. Forneça instrumento, local de referência, moeda, lado, horários com fuso, validade escolhida, capital de referência, orçamento monetário de risco, teto de nocional, entrada, stop, alvo, lote, multiplicador e custos. Para long, `equity` é o capital que o cenário trata como caixa disponível para entrada e seus custos; não use patrimônio indisponível ou já comprometido como se fosse caixa livre. O motor não consulta saldo, posições ou compromissos existentes. Use alias para qualquer dado pessoal desnecessário. A autenticidade da fonte e a adequação ao usuário não são verificadas pelo motor.

Ao mudar uma premissa, solicite novo cálculo e compare o novo hash de entrada. Não peça “liberar operação”: o projeto termina no estudo e na revisão. Um diário de operações, persistência e conectores de mercado não fazem parte desta primeira versão.
