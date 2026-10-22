# Segurança e limites

## Modelo de ameaças

Entrada não confiável pode tentar enviar números não finitos, campos de execução, JSON duplicado, conteúdo enorme, fonte falsa ou horário manipulado. O contrato fechado e a CLI limitam a superfície. O processo lê o arquivo que o próprio operador escolhe; não é serviço de upload nem isolamento para executar código desconhecido.

O motor não faz rede, shell, importação dinâmica por entrada, gravação de conta ou ordem. Informações de fonte e hash não autenticam um provedor. Uma modificação maliciosa do código ou do ambiente pode alterar o resultado; testes não substituem revisão da revisão exata utilizada.

Entradas e resultados podem revelar patrimônio e estratégia. Use exemplos fictícios no repositório público; mantenha dados reais fora de commits. Não envie segredos ao ChatGPT nem ao JSON. A rejeição de campos desconhecidos reduz erros, mas não detecta todos os segredos colocados em campos de texto permitidos.

## Controles e limitações

Números finitos, validade temporal relativa, limite de arquivo e schema estrito são controles de código. Revisão humana, adequação, proteção da conta GitHub e disponibilidade de dados são responsabilidades externas. Não há login, RLS, assinatura de evidência, aprovação autenticada, proteção automática de branch ou conformidade certificada neste pacote.

Os testes de superfície por AST são uma verificação de regressão de imports/chamadas proibidos, não uma sandbox ou prova de ausência de vulnerabilidades. Nenhuma análise de CVE externa é necessária para dependências runtime porque não existem; versões de Python e Actions ainda exigem manutenção.

## Relatar problema

Não publique dados financeiros ou credenciais em issues. Quando disponível, use o canal privado do GitHub Security Advisory; se não estiver disponível, solicite ao proprietário um canal privado antes de compartilhar detalhes sensíveis. A criação deste arquivo não ativa esse canal nem promete prazo de resposta.
