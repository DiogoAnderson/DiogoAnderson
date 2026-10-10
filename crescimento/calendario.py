"""Monta a grade semanal "1 ideia -> 4 redes" com horários do Metricool.

Cada ideia vira peças nativas em cada rede, publicadas em horários diferentes
(nada de postar o mesmo arquivo no mesmo minuto em todas). A saída é uma lista
de dicionários no formato que a rotina diária entrega ao createScheduledPost do Metricool.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path

DADOS = Path(__file__).parent / "dados"

# Pilares do calendário editorial do autor (segunda, quarta, sexta) + dias de reforço.
PILAR_DO_DIA = {
    0: "RH e Governança",
    1: "Dr. Di (série de educação financeira com humor)",
    2: "Educação Financeira",
    3: "Bastidor com lição (evento, palestra, cliente)",
    4: "Lições de Vida",
    5: "Caixinha de perguntas / resposta a comentário",
    6: None,  # domingo: descanso, só stories
}

DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]

# Formato por rede: o que cada algoritmo premia hoje.
FORMATOS = {
    "instagram": "REEL (30-60s) — às terças e quintas como TRIAL_REEL para testar gancho com não seguidores",
    "tiktok": "vídeo 31-90s com palavra-chave falada nos 3 primeiros segundos e na legenda",
    "youtube": "short (até 60s) com 'vídeo relacionado' apontando para o episódio longo",
    "linkedin": "texto até 1.500 caracteres ou carrossel em PDF; link só no 1º comentário",
}


@dataclass
class Peca:
    data_hora: str
    rede: str
    pilar: str
    formato: str
    instagram_tipo: str | None = None


def _horarios() -> dict:
    return json.loads((DADOS / "melhores_horarios.json").read_text(encoding="utf-8"))


def grade_semana(segunda: date) -> list[Peca]:
    """Gera a grade de segunda a sábado a partir da segunda-feira informada."""
    if segunda.weekday() != 0:
        raise ValueError("A grade começa numa segunda-feira")
    h = _horarios()
    pecas: list[Peca] = []
    for i in range(7):
        dia = segunda + timedelta(days=i)
        pilar = PILAR_DO_DIA[dia.weekday()]
        if pilar is None:
            continue
        # Instagram e TikTok no pico da manhã com 30 min de diferença;
        # YouTube no pico da tarde; LinkedIn só em dia útil, cedo.
        slots = [
            ("instagram", time(h["instagram"]["pico_manha"], 0)),
            ("tiktok", time(h["tiktok"]["pico_manha"], 30)),
            ("youtube", time(h["youtube"]["pico_tarde"], 0)),
        ]
        if dia.weekday() < 5:
            slots.append(("linkedin", time(h["linkedin"]["pico_manha"], 0)))
        for rede, hora in slots:
            tipo = None
            if rede == "instagram":
                tipo = "TRIAL_REEL" if dia.weekday() in (1, 3) else "REEL"
            pecas.append(Peca(datetime.combine(dia, hora).isoformat(), rede, pilar, FORMATOS[rede], tipo))
    return sorted(pecas, key=lambda p: p.data_hora)


def como_markdown(pecas: list[Peca]) -> str:
    linhas = ["| Quando | Rede | Pilar | Formato |", "|---|---|---|---|"]
    for p in pecas:
        dt = datetime.fromisoformat(p.data_hora)
        quando = f"{DIAS[dt.weekday()]} {dt:%d/%m %Hh%M}"
        formato = p.instagram_tipo or p.formato.split(" ")[0]
        linhas.append(f"| {quando} | {p.rede} | {p.pilar} | {formato} |")
    return "\n".join(linhas) + "\n"


def proxima_segunda(hoje: date | None = None) -> date:
    hoje = hoje or date.today()
    return hoje + timedelta(days=(7 - hoje.weekday()) % 7 or 7)


if __name__ == "__main__":
    import sys

    inicio = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else proxima_segunda()
    grade = grade_semana(inicio)
    if "--json" in sys.argv:
        print(json.dumps([asdict(p) for p in grade], ensure_ascii=False, indent=2))
    else:
        print(como_markdown(grade))
