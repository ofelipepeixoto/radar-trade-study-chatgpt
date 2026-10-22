# Roadmap por evidência

| Fase | Critério de saída | Estado desta entrega |
| --- | --- | --- |
| 0 — Diligência | Código/licença do upstream e sobreposição mapeados | Relatório integrado em `main` pela PR #1 |
| 1 — Fatia funcional | Cenário fictício reproduzível, contrato e testes negativos | Motor, instruções e testes integrados em `main` pela PR #2 |
| 2 — Hardening | Revisão independente, correções e CI observada | 24 testes e 981 cenários conferidos; evidências em [VALIDATION.md](docs/VALIDATION.md) |
| 3 — Integração | Contrato estável e consumidor real | Futura; sem conexão ativa |
| 4 — Observabilidade | Problema operacional demonstra necessidade | JSON por execução já disponível; sem monitor |
| 5 — Evals | Casos versionados de uso com e sem runner | Teste de instruções humano ainda pendente |
| 6 — Produção | Revisão de adequação, direitos, segurança e operação | Fora do MVP |
| 7 — Escala | Medidas de concorrência e uso justificam serviço | Sem benchmark ou promessa de escala |
| 8 — Produto | Demanda e disposição a pagar verificadas | Hipótese, sem cobrança |

Próxima prioridade: homologar com um operador o exemplo fictício no ChatGPT e o caminho sem ferramenta de execução. Diário, importação e integração só entram após evidência de uso. Não implementar sinais automáticos, trading, custódia ou agente transacional neste produto.
