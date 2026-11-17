# evitarodizio

Calcula rotas que evitam a área de rodízio de São Paulo, com base no final da placa e no horário previsto de chegada. Uso pessoal.

Plano completo e fases: `plano_app_rodizio.md`.

## Status

- **Fase 1 (regras do rodízio):** função `esta_em_rodizio` implementada e testada com regras de exemplo. As regras reais ainda não foram preenchidas.

## Regras do rodízio

As faixas ficam em `rodizio/regras.json`. O arquivo começa com `"status": "pendente"`, e o código recusa usá-lo até que as faixas e feriados sejam conferidos com o CET (https://www.cetsp.com.br) e o status seja alterado para `"verificado"`.

Formato de cada faixa:

```json
{ "dias": [0, 1, 2, 3, 4], "inicio": "07:00", "fim": "10:00", "finais": [1, 2] }
```

- `dias`: 0 = segunda ... 6 = domingo
- `inicio` (inclusivo) e `fim` (exclusivo), no formato `HH:MM`
- `finais`: últimos dígitos da placa que são restritos nessa faixa
- `feriados`: lista de datas `AAAA-MM-DD` sem restrição

## Uso

```python
from datetime import datetime
from rodizio import esta_em_rodizio, carregar_regras

resultado = esta_em_rodizio(final_placa=1, data_hora=datetime(2026, 11, 16, 9, 30))
print(resultado.restrito, resultado.proximo_livre)
```

Sem o argumento `regras`, a função carrega `regras.json` e exige que esteja verificado.

## Testes

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

Os testes usam regras de exemplo (fixture), não as regras do CET. Eles validam bordas de faixa, virada de dia, feriados, fim de semana e busca do próximo horário livre.
