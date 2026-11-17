"""Testes da função de rodízio.

Usam regras de exemplo (FIXTURE), não as regras do CET. Servem para validar
a lógica: bordas de faixa, virada de dia, feriados e busca do próximo horário.
"""

from datetime import datetime

import pytest

from rodizio import RegrasNaoVerificadas, carregar_regras, esta_em_rodizio

# 0 = segunda ... 6 = domingo
FIXTURE = {
    "status": "verificado",
    "faixas": [
        {"dias": [0, 1, 2, 3, 4], "inicio": "07:00", "fim": "10:00", "finais": [1, 2]},
        {"dias": [0, 1, 2, 3, 4], "inicio": "17:00", "fim": "20:00", "finais": [1, 2]},
    ],
    "feriados": ["2026-11-20"],
}

# 2026-11-16 é segunda-feira
SEGUNDA = datetime(2026, 11, 16)


def dt(h, m=0, dia=SEGUNDA):
    return dia.replace(hour=h, minute=m)


def test_inicio_da_faixa_e_restrito():
    assert esta_em_rodizio(1, dt(7, 0), FIXTURE).restrito


def test_fim_da_faixa_nao_e_restrito():
    # fim é exclusivo: 10:00 já está livre
    assert not esta_em_rodizio(1, dt(10, 0), FIXTURE).restrito


def test_um_minuto_antes_do_fim_ainda_e_restrito():
    assert esta_em_rodizio(1, dt(9, 59), FIXTURE).restrito


def test_antes_do_inicio_nao_e_restrito():
    assert not esta_em_rodizio(1, dt(6, 59), FIXTURE).restrito


def test_final_nao_restrito_na_mesma_faixa():
    assert not esta_em_rodizio(5, dt(8, 0), FIXTURE).restrito


def test_segunda_faixa_do_dia():
    assert esta_em_rodizio(2, dt(18, 0), FIXTURE).restrito
    assert not esta_em_rodizio(2, dt(20, 0), FIXTURE).restrito


def test_fim_de_semana_nao_e_restrito():
    sabado = datetime(2026, 11, 21, 8, 0)
    assert not esta_em_rodizio(1, sabado, FIXTURE).restrito


def test_feriado_nao_e_restrito():
    feriado = datetime(2026, 11, 20, 8, 0)  # sexta-feira, data na lista
    assert not esta_em_rodizio(1, feriado, FIXTURE).restrito


def test_virada_de_dia_sem_restricao_a_noite():
    assert not esta_em_rodizio(1, datetime(2026, 11, 16, 23, 59), FIXTURE).restrito
    assert not esta_em_rodizio(1, datetime(2026, 11, 17, 0, 1), FIXTURE).restrito


def test_proximo_livre_ao_sair_da_faixa():
    r = esta_em_rodizio(1, dt(9, 30), FIXTURE)
    assert r.restrito
    assert r.proximo_livre == dt(10, 0)


def test_proximo_livre_pula_para_proximo_dia_util_se_necessario():
    # sexta 19:30 com final 1: restrito até 20:00, livre depois
    sexta = datetime(2026, 11, 19, 19, 30)
    r = esta_em_rodizio(1, sexta, FIXTURE)
    assert r.restrito
    assert r.proximo_livre == datetime(2026, 11, 19, 20, 0)


def test_livre_nao_tem_proximo_livre():
    r = esta_em_rodizio(5, dt(8, 0), FIXTURE)
    assert r.proximo_livre is None


@pytest.mark.parametrize("final", [-1, 10])
def test_final_invalido(final):
    with pytest.raises(ValueError):
        esta_em_rodizio(final, dt(8, 0), FIXTURE)


def test_data_com_fuso_e_recusada():
    from datetime import timezone

    with pytest.raises(ValueError):
        esta_em_rodizio(1, dt(8, 0).replace(tzinfo=timezone.utc), FIXTURE)


def test_regras_pendentes_nao_sao_usadas(tmp_path):
    arq = tmp_path / "regras.json"
    arq.write_text('{"status": "pendente", "faixas": [], "feriados": []}', encoding="utf-8")
    with pytest.raises(RegrasNaoVerificadas):
        carregar_regras(arq)


def test_config_real_no_repositorio_ainda_nao_verificada():
    # Garante que nada roda com regras não conferidas até o preenchimento.
    with pytest.raises(RegrasNaoVerificadas):
        carregar_regras()
