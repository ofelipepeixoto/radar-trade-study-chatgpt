# Direção visual do Radar Trade Study

Esta é uma proposta autoral para documentação e uma possível interface futura. A experiência entregue nesta versão usa Markdown, JSON e CLI; não há componentes web, logo oficial ou tema do ChatGPT instalado.

## Princípios

Priorizar leitura de premissas, unidades e evidências. Uma ação principal por etapa. Mostrar incerteza de forma concreta: dado faltante, origem não verificada ou validade ultrapassada. Evitar painéis decorativos, placares de confiança, animações de mercado e aparência de terminal de execução.

## Tokens propostos

| Token | Valor proposto | Uso |
| --- | --- | --- |
| `surface` | `#F7F8FA` | Fundo neutro em interface futura. |
| `surface-raised` | `#FFFFFF` | Área de leitura e formulários. |
| `text` | `#17212B` | Texto principal. |
| `text-muted` | `#425466` | Ajuda e metadados. |
| `accent` | `#1F4F70` | Ação de revisão e links. |
| `attention` | `#7A4600` | Dados incompletos ou vencidos, sempre com texto. |
| `error` | `#9D1C20` | Erro de validação, sempre com mensagem específica. |
| `border` | `#C5CDD5` | Separação de campos e tabelas. |

São valores propostos; contraste visual e comportamento não foram testados em interface. Não transferir automaticamente a identidade de outro projeto ou do plugin de UX.

## Tipografia e composição

Usar fontes de sistema sem dependência externa. Corpo de leitura com no mínimo 16 px em uma futura UI, títulos curtos e números tabulares quando disponíveis. Escala de espaçamento proposta: 4, 8, 12, 16, 24 e 32 px. Conteúdo principal em coluna legível; tabelas para comparações exatas e campos agrupados por tarefa.

O resultado começa pelo estado, seguido de dados de referência, entradas, cálculo, limites e evidência. Para long, agrupar nocional, custo de entrada, desembolso inicial e caixa restante com rótulos distintos; não apresentar saldo modelado como saldo real de conta. Em telas estreitas, converter tabelas extensas em grupos de rótulo e valor preservando unidade e significado. O arquivo JSON original permanece a fonte para reproduzir o cálculo.

## Componentes futuros e estados

Se uma interface for implementada, usar somente: seletor de tarefa, grupos de campos, resumo de validação, tabela de premissas, resultado com unidades e painel de evidência. Rótulos, ajuda e erro devem permanecer associados ao campo. Nenhum componente externo foi incorporado nem precisa ser instalado para usar esta versão.

Manter texto de estado conforme `docs/UX.md`. Não usar cor ou ícone isolado. `ok` recebe rótulo neutro “Cenário calculado”; não usar selo “aprovado” ou “seguro”. Snapshot fictício deve estar identificado antes do primeiro número.

## Acessibilidade e movimento

Uma implementação futura precisa verificar contraste, zoom, leitura por tecnologia assistiva, teclado e foco visível. Não há animação necessária; se for adicionada, respeitar movimento reduzido e manter função sem efeitos. Estes requisitos são critérios de aceite, não declaração de conformidade.

## Procedência e limites

Proposta original deste projeto, sem cópia de assets, logos ou componentes de terceiros. A documentação define direção e termos; não comprova frontend, integração, persistência ou teste de usabilidade.
