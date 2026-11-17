"""Área do mini-anel viário (Centro Expandido), a partir do GeoJSON do CET."""

from __future__ import annotations

import json
from pathlib import Path

AREA_PADRAO = Path(__file__).with_name("area_rodizio.geojson")


def carregar_anel(caminho: Path = AREA_PADRAO) -> list[tuple[float, float]]:
    """Retorna o anel externo como lista de (lon, lat)."""
    geo = json.loads(caminho.read_text(encoding="utf-8"))
    anel = geo["features"][0]["geometry"]["coordinates"][0]
    return [(float(lon), float(lat)) for lon, lat in anel]


def ponto_no_poligono(lon: float, lat: float, anel: list[tuple[float, float]]) -> bool:
    """Ray casting: conta cruzamentos de um raio horizontal com as arestas."""
    dentro = False
    n = len(anel)
    j = n - 1
    for i in range(n):
        xi, yi = anel[i]
        xj, yj = anel[j]
        if (yi > lat) != (yj > lat):
            x_cruz = xi + (lat - yi) * (xj - xi) / (yj - yi)
            if lon < x_cruz:
                dentro = not dentro
        j = i
    return dentro


def esta_na_area(lon: float, lat: float, anel: list[tuple[float, float]] | None = None) -> bool:
    """True se o ponto (lon, lat) estiver dentro do mini-anel."""
    if anel is None:
        anel = carregar_anel()
    return ponto_no_poligono(lon, lat, anel)
