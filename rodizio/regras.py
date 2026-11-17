"""Regras do rodízio: função pura que verifica se um carro está restrito.

Nenhuma regra real fica codificada aqui. As faixas vêm de um arquivo de
configuração (regras.json), que só é usado depois de marcado como verificado.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any

CONFIG_PADRAO = Path(__file__).with_name("regras.json")
STATUS_VERIFICADO = "verificado"
DIAS_PROCURA = 7  # quantos dias à frente procurar o próximo horário livre


class RegrasNaoVerificadas(RuntimeError):
    """Regras ainda não conferidas com o calendário oficial do CET."""


@dataclass(frozen=True)
class Resultado:
    restrito: bool
    motivo: str
    proximo_livre: datetime | None


def carregar_regras(caminho: Path = CONFIG_PADRAO) -> dict[str, Any]:
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    if dados.get("status") != STATUS_VERIFICADO:
        raise RegrasNaoVerificadas(
            "regras.json ainda não foi conferido com o CET. "
            "Preencha as faixas e altere status para 'verificado'."
        )
    return dados


def _hora(texto: str) -> time:
    return time.fromisoformat(texto)


def _restrito_em(final_placa: int, momento: datetime, regras: dict[str, Any]) -> str | None:
    """Retorna o motivo da restrição no momento, ou None se estiver livre."""
    if momento.date().isoformat() in regras.get("feriados", []):
        return None

    for faixa in regras["faixas"]:
        if momento.weekday() not in faixa["dias"]:
            continue
        if final_placa not in faixa["finais"]:
            continue
        if _hora(faixa["inicio"]) <= momento.time() < _hora(faixa["fim"]):
            return f"final {final_placa} em faixa restrita {faixa['inicio']}-{faixa['fim']}"
    return None


def esta_em_rodizio(
    final_placa: int,
    data_hora: datetime,
    regras: dict[str, Any] | None = None,
) -> Resultado:
    """Verifica se o carro estará restrito no horário previsto.

    final_placa: último dígito da placa (0 a 9).
    data_hora: horário previsto de chegada na área.
    regras: dicionário de regras. Se None, carrega regras.json verificado.
    """
    if not 0 <= final_placa <= 9:
        raise ValueError("final_placa deve estar entre 0 e 9")
    if data_hora.tzinfo is not None:
        raise ValueError("data_hora deve ser ingênua (horário local de São Paulo)")

    if regras is None:
        regras = carregar_regras()

    motivo = _restrito_em(final_placa, data_hora, regras)
    if motivo is None:
        return Resultado(restrito=False, motivo="livre no horário informado", proximo_livre=None)

    proximo = _proximo_livre(final_placa, data_hora, regras)
    return Resultado(restrito=True, motivo=motivo, proximo_livre=proximo)


def _proximo_livre(final_placa: int, inicio: datetime, regras: dict[str, Any]) -> datetime | None:
    """Primeiro minuto, a partir de `inicio`, em que o carro não está restrito."""
    limite = inicio + timedelta(days=DIAS_PROCURA)
    candidato = inicio.replace(second=0, microsecond=0)
    while candidato <= limite:
        if _restrito_em(final_placa, candidato, regras) is None:
            return candidato
        candidato += timedelta(minutes=1)
    return None
