# Regras de desenvolvimento

- Ler README, docs/CONTRACT.md e SECURITY.md antes de mudar o domínio.
- Manter cálculo offline e determinístico. Nunca adicionar executor, credenciais, rede, transações, telemetria ou instalação automática como consequência de um arquivo de entrada.
- Não copiar código de outros projetos sem verificar licença. Não importar scripts do upstream no caminho de runtime.
- Entrada financeira usa Decimal finito. Não aceitar float, bool como número, campos desconhecidos ou valores JSON não padronizados.
- Não selecionar risco, capital, preços ou custos pelo usuário. `ok` é cálculo condicional, não autorização.
- Alterar contrato, exemplo, testes e documentação juntos quando o comportamento mudar.
- Não adicionar dependência ou servidor sem explicar necessidade e alternativa mais simples.
- Validar com `PYTHONPATH=src python -m unittest discover -s tests -v`, `python -m compileall -q src tests` e `python scripts/check_offline.py`.
- Separar teste executado, inspeção estática e pendência. Não afirmar integração ou rentabilidade por causa de testes aritméticos.
- Trabalhar em branch e PR revisável. Não fazer merge, deploy ou mudança de acesso sem autorização aplicável e revisão humana.
