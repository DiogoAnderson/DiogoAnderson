from datetime import date

import pytest

from crescimento import calendario, cortes, diagnostico

SRT = """1
00:00:00,000 --> 00:00:04,000
Bom dia, pessoal.

2
00:00:04,000 --> 00:00:09,000
Você sabia que 82% das famílias têm dívida?

3
00:00:09,000 --> 00:00:30,000
E o pior é que ninguém fala disso no trabalho.

4
00:00:30,000 --> 00:00:40,000
Então vamos conversar.
"""


def test_diagnostico_le_dados_reais():
    ig = diagnostico.analisar_instagram(diagnostico.carregar("instagram"))
    assert ig["total"] > 50
    assert ig["mediana_views_gancho_forte"] > ig["mediana_views_gancho_fraco"]
    assert "# Diagnóstico" in diagnostico.relatorio()


def test_pilar_por_palavra_chave():
    post = diagnostico.Post(None, 0, "Cuidado com o golpe do Pix", {})
    assert post.pilar == "educação financeira"


def test_grade_semana_tem_seis_dias_e_trial_reels():
    grade = calendario.grade_semana(date(2026, 10, 12))
    dias = {p.data_hora[:10] for p in grade}
    assert len(dias) == 6  # domingo fica de fora
    assert any(p.instagram_tipo == "TRIAL_REEL" for p in grade)
    assert not any(p.rede == "linkedin" and p.data_hora.startswith("2026-10-17") for p in grade)


def test_grade_exige_segunda():
    with pytest.raises(ValueError):
        calendario.grade_semana(date(2026, 10, 13))


def test_cortes_escolhem_frase_com_gancho():
    legendas = cortes.ler_srt(SRT)
    assert len(legendas) == 4
    achados = cortes.sugerir_cortes(legendas, duracao_min=20, duracao_max=40)
    assert achados[0].gancho.startswith("Você sabia")
    assert achados[0].fim - achados[0].inicio >= 20
    cmd = cortes.comando_ffmpeg("live.mp4", achados[0], "c1.mp4")
    assert "-ss 4.00" in cmd and "1080:1920" in cmd
