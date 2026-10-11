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


def test_grade_segue_a_grade_oficial():
    grade = calendario.grade_semana(date(2026, 10, 12))
    reels = {p.data_hora: p.pilar for p in grade if p.instagram_tipo == "REEL"}
    assert reels["2026-10-13T18:00:00"] == "Radar Cooperativo"
    assert reels["2026-10-16T10:00:00"] == "Doutor Di"
    trials = [p.data_hora for p in grade if p.instagram_tipo == "TRIAL_REEL"]
    assert trials == ["2026-10-14T18:00:00", "2026-10-15T18:00:00"]
    assert not any(p.data_hora >= "2026-10-17" for p in grade)  # fim de semana só Stories
    assert not any(p.rede == "linkedin" and p.pilar == "Doutor Di" for p in grade)
    horarios = [(p.rede, p.data_hora) for p in grade]
    assert len(horarios) == len(set(horarios))  # nenhuma rede com dois posts no mesmo horário


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


def test_pecas_monta_url_com_foto_local_e_acentos():
    from crescimento import pecas

    url = pecas.montar_url("capa", {"foto": "marca/banner-farol.png", "selo": "Educação Financeira", "gancho": "Três notícias", "apoio": ""})
    assert url.startswith("file://") and "capa-reel.html?" in url
    assert "foto=file%3A%2F%2F" in url and "Educa%C3%A7%C3%A3o" in url
    assert "apoio=" not in url
