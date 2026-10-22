# Radar Trade Study ChatGPT

Estudos condicionais de risco em português, com cálculos determinísticos offline e arquivos utilizáveis no ChatGPT. Implementação autoral de Carlos Felipe, inspirada no estudo público de `day-trader-skill`, sem importar seus scripts ou suas instruções para Claude.

**Experimental e consultivo.** `ok` significa que o cálculo de um cenário passou nas validações implementadas. Não indica oportunidade de mercado, adequação pessoal, aprovação ou ordem de negociação.

## Comece aqui

O motor, as instruções, os testes e a auditoria estão disponíveis na branch `main`.

| Objetivo | Arquivo ou pasta |
| --- | --- |
| Configurar e usar no ChatGPT | [Guia passo a passo](docs/USAR-NO-CHATGPT.md) |
| Copiar as instruções do Projeto | [INSTRUCOES.md](INSTRUCOES.md) |
| Entender entradas, fórmulas e resultados | [Contrato do cenário](docs/CONTRACT.md) |
| Estudar um exemplo fictício | [scenario-long.json](examples/scenario-long.json) |
| Consultar o motor e a interface de execução | [Código Python](src/radar_trade_study/) |
| Conferir testes e evidências | [Testes](tests/) e [validação](docs/VALIDATION.md) |
| Ler a auditoria em 30 seções | [Relatório técnico](docs/audit/2026-10-22-day-trader-skill.md) |

## Primeiro resultado

Com Python 3.11 ou superior, a partir da raiz:

```bash
PYTHONPATH=src python -m radar_trade_study examples/scenario-long.json
PYTHONPATH=src python -m unittest discover -s tests -v
```

No PowerShell, configure primeiro `$env:PYTHONPATH = "src"` e execute os mesmos comandos Python, sem o prefixo `PYTHONPATH=src`.

O exemplo usa dados fictícios. O resultado é JSON e inclui origem declarada, horários, hash da entrada, quantidade, nocional, perda modelada e relação ganho/risco após custos. Consulte [o contrato](docs/CONTRACT.md) para campos, fórmulas, estados e códigos de saída.

## Usar pelo ChatGPT

Siga [o guia com passos](docs/USAR-NO-CHATGPT.md). Use [INSTRUCOES.md](INSTRUCOES.md) como instruções do projeto e disponibilize contrato, exemplo e código. Peça explicitamente a execução do exemplo quando houver ambiente Python. Sem ferramenta de execução, o assistente deve explicar o cenário e declarar que o motor não foi executado.

Este repositório não cria automaticamente um Projeto, plugin ou conexão MCP no ChatGPT. A disponibilidade de arquivos e código depende do ambiente da conversa. Não há sincronização automática com GitHub implementada aqui.

## O que está implementado

- Entrada JSON fechada, números decimais finitos e validação de horários.
- Dimensionamento linear por orçamento monetário de risco e teto de nocional, ambos escolhidos explicitamente pelo operador.
- Custos conservadores de entrada e saída, multiplicador e arredondamento por lote.
- Bloqueio de quantidade em dado vencido e resultado sem cenário válido quando os limites inviabilizam o cálculo.
- Instruções para revisão humana e separação entre fato, evidência, inferência e proposta.

## Limites

Não coleta cotações nem confirma a autenticidade de fontes. O hash identifica conteúdo, não autor ou horário real. O par `observed_at`/`evaluated_at` mede validade relativa declarada; um cenário histórico não se torna atual por passar nessa verificação.

O modelo é linear. Não cobre contratos inversos, opções, margem, liquidação, financiamento, empréstimo de ativos, impostos ou microestrutura. Estudo short não comprova disponibilidade de aluguel. Stop e custos modelados não limitam a perda real em gaps, falhas ou falta de liquidez.

Não há escolha de ativos, indicadores técnicos, backtest, previsão, probabilidade de lucro, diário persistente, autenticação, multiusuário, serviço web, API, MCP, agendador, alertas ou executor. Não recebe chaves, não instala bots e não chama corretoras. Instruções textuais não substituem controles em outros sistemas.

## Arquitetura e desenvolvimento

Python e biblioteca padrão: sem dependências de runtime, banco, VPS ou API paga. Veja [arquitetura](ARCHITECTURE.md), [segurança](SECURITY.md), [regras de contribuição](CONTRIBUTING.md), [roadmap](ROADMAP.md) e [validação](docs/VALIDATION.md).

CI executa testes, compilação, verificação de superfície offline, comparação com aritmética racional e reprodução do exemplo em Python 3.11/3.12. Consulte as [execuções reais no GitHub](https://github.com/ofelipepeixoto/radar-trade-study-chatgpt/actions/workflows/checks.yml).

## Origem e direitos

Código novo sob [MIT](LICENSE), copyright Carlos Felipe. [NOTICE.md](NOTICE.md) registra o estudo e os limites da referência externa. O conteúdo comercial vinculado no pedido não foi reutilizado. A [auditoria pública em 30 seções](docs/audit/2026-10-22-day-trader-skill.md) e a implementação foram integradas pelas [PR #1](https://github.com/ofelipepeixoto/radar-trade-study-chatgpt/pull/1) e [PR #2](https://github.com/ofelipepeixoto/radar-trade-study-chatgpt/pull/2). Essa integração não implica homologação financeira ou integração de outros projetos; a validação com um operador em nova conversa ChatGPT permanece pendente.
