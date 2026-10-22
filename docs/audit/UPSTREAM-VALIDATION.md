# Validação do upstream em 22/10/2026

Revisão: `Jakeschincariol/day-trader-skill@3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd`.

Após inspeção dos módulos e testes, executou-se `unittest` com as fixtures do próprio upstream, em processo com ambiente limpo, sem credenciais, limite de 120 segundos e audit hook bloqueando sockets, `subprocess.Popen`, `os.system` e spawn. Não houve instalação de dependências, HTTP ou ordens. O hook é precaução para esse ensaio, não isolamento robusto para código hostil.

Resultado observado: **315 testes, 11,618 segundos, OK, exit 0**. Isso demonstra a suíte fornecida nessa configuração, não todos os comportamentos possíveis. Três casos adicionais falharam nas expectativas de segurança/correção apesar da suíte verde:

| Caso | Resultado reproduzido | Consequência |
| --- | --- | --- |
| notional `NaN` | `PASS`, valores derivados não finitos | Comparações de limites não bloqueiam a entrada inválida |
| Opening range com uma de três barras | `complete=true`, `triggered` | Range incompleto pode ser tratado como rompimento válido |
| ATR manual histórico sem entry-bar | 14 barras / ATR 1,966 versus corte 8: 9 barras / ATR 3,2182 | Plano usa observações posteriores à hora declarada |

O [script de reprodução](reproduce_upstream.py) contém apenas o ensaio autoral. Ele exige obter separadamente e revisar a revisão upstream indicada; não faz download nem importa o upstream no produto. Rodar código externo somente em ambiente descartável sem segredos. Exemplo, após essa preparação:

```bash
python docs/audit/reproduce_upstream.py /caminho/para/upstream-revisado
```

Os testes da implementação própria ficam em `tests/`, em PR independente. Não se confundem com a suíte upstream e não estabelecem rentabilidade, homologação no ChatGPT ou produção.
