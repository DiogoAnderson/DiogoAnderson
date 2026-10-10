"""Transforma um vídeo longo (live, entrevista, palestra) em cortes verticais.

Entrada: o vídeo e a legenda .srt (gerada no CapCut, YouTube Studio ou Whisper).
Saída: os trechos com mais cara de gancho e os comandos ffmpeg prontos para cortar em 9:16.

O critério imita o que segura alguém nos 3 primeiros segundos: pergunta direta,
número, conflito, "você" e promessa de revelação. Um episódio de 10 minutos que hoje
fica nas 100 views no TikTok vira 4 a 6 cortes de 30-60s, o formato que tem rendido o dobro.
"""

from __future__ import annotations

import re
import shlex
from dataclasses import dataclass

GATILHOS = {
    r"\?": 2,
    r"\d": 2,
    r"\bvocê\b|\bvc\b|\bseu\b|\bsua\b": 1,
    r"\bnunca\b|\bninguém\b|\berro\b|\bgolpe\b|\bcuidado\b|\bproblema\b|\bverdade\b|\bsegredo\b": 2,
    r"\bpor que\b|\bporque\b|\bcomo\b": 1,
    r"\bdinheiro\b|\bdívida\b|\bcartão\b|\bsalário\b|\bboleto\b|\bjuros\b": 1,
}


@dataclass
class Legenda:
    inicio: float
    fim: float
    texto: str


@dataclass
class Corte:
    inicio: float
    fim: float
    gancho: str
    nota: int


def _segundos(carimbo: str) -> float:
    h, m, resto = carimbo.strip().replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(resto)


def ler_srt(conteudo: str) -> list[Legenda]:
    blocos = re.split(r"\n\s*\n", conteudo.strip())
    legendas = []
    for bloco in blocos:
        linhas = [l for l in bloco.splitlines() if l.strip()]
        tempo = next((l for l in linhas if "-->" in l), None)
        if not tempo:
            continue
        ini, fim = tempo.split("-->")
        texto = " ".join(linhas[linhas.index(tempo) + 1:])
        legendas.append(Legenda(_segundos(ini), _segundos(fim), texto))
    return legendas


def nota_gancho(texto: str) -> int:
    t = texto.lower()
    return sum(peso for padrao, peso in GATILHOS.items() if re.search(padrao, t))


def sugerir_cortes(legendas: list[Legenda], duracao_min: float = 25, duracao_max: float = 60,
                   quantidade: int = 6) -> list[Corte]:
    """Escolhe as frases com mais cara de gancho e estende cada corte até fechar a ideia."""
    candidatos = []
    for i, leg in enumerate(legendas):
        nota = nota_gancho(leg.texto)
        if nota < 3:
            continue
        fim = leg.fim
        j = i
        while j + 1 < len(legendas) and legendas[j + 1].fim - leg.inicio <= duracao_max:
            j += 1
            fim = legendas[j].fim
            # Para no fim de frase depois de atingir a duração mínima.
            if fim - leg.inicio >= duracao_min and legendas[j].texto.rstrip().endswith((".", "!", "?")):
                break
        if fim - leg.inicio >= duracao_min:
            candidatos.append(Corte(leg.inicio, fim, leg.texto, nota))
    escolhidos: list[Corte] = []
    for c in sorted(candidatos, key=lambda c: c.nota, reverse=True):
        if all(c.fim <= e.inicio or c.inicio >= e.fim for e in escolhidos):
            escolhidos.append(c)
        if len(escolhidos) == quantidade:
            break
    return sorted(escolhidos, key=lambda c: c.inicio)


def comando_ffmpeg(video: str, corte: Corte, saida: str) -> str:
    """Corta e enquadra em 1080x1920 pelo centro. Legenda queimada fica com o CapCut (auto-legenda)."""
    return (f"ffmpeg -y -ss {corte.inicio:.2f} -to {corte.fim:.2f} -i {shlex.quote(video)} "
            f"-vf \"crop=ih*9/16:ih,scale=1080:1920\" -c:v libx264 -crf 20 -c:a aac {shlex.quote(saida)}")


if __name__ == "__main__":
    import sys
    from pathlib import Path

    if len(sys.argv) < 3:
        sys.exit("uso: python -m crescimento.cortes VIDEO.mp4 LEGENDA.srt")
    video, srt = sys.argv[1], sys.argv[2]
    cortes = sugerir_cortes(ler_srt(Path(srt).read_text(encoding="utf-8")))
    for n, c in enumerate(cortes, 1):
        print(f"# Corte {n} ({c.fim - c.inicio:.0f}s, nota {c.nota}): {c.gancho}")
        print(comando_ffmpeg(video, c, f"corte_{n:02d}.mp4"))
