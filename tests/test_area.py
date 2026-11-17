"""Testes da área do mini-anel com pontos de controle.

Sé (centro) deve estar dentro. Aeroporto de Guarulhos e Interlagos devem estar fora.
"""

import pytest

from rodizio.area import carregar_anel, esta_na_area

ANEL = carregar_anel()


def test_anel_fechado_e_com_pontos_suficientes():
    assert ANEL[0] == ANEL[-1]
    assert len(ANEL) > 100


@pytest.mark.parametrize(
    "nome, lon, lat",
    [
        ("Praça da Sé", -46.6333, -23.5505),
        ("Praça da República", -46.6418, -23.5437),
    ],
)
def test_pontos_do_centro_estao_dentro(nome, lon, lat):
    assert esta_na_area(lon, lat, ANEL), nome


@pytest.mark.parametrize(
    "nome, lon, lat",
    [
        ("Aeroporto de Guarulhos", -46.4730, -23.4356),
        ("Autódromo de Interlagos", -46.6972, -23.7036),
    ],
)
def test_pontos_distantes_estao_fora(nome, lon, lat):
    assert not esta_na_area(lon, lat, ANEL), nome
