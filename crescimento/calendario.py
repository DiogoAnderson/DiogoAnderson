"""Monta a grade semanal do Master Growth: um vídeo vira peças nativas em cada rede.

Espelha a seção 3 do MASTER-GROWTH.md (pasta _Master-Growth no Drive), que é a fonte de
verdade. Cada quadro sai em horários diferentes por rede, nunca o mesmo arquivo no mesmo
minuto em todas.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timedelta


# Grade oficial do Master Growth (MASTER-GROWTH.md, seção 3). Sábado e domingo: só Stories.
QUADRO_DO_DIA = {
    0: ("Lições de Vida", time(10, 0)),
    1: ("Radar Cooperativo", time(18, 0)),
    2: ("Educação Financeira", time(10, 0)),
    3: ("RH e Governança", time(10, 0)),
    4: ("Doutor Di", time(10, 0)),
}

DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]

# Formato por rede: o que cada algoritmo premia hoje.
FORMATOS = {
    "instagram": "REEL com o vídeo inteiro",
    "instagram_trial": "TRIAL_REEL com o corte e o gancho B (experimento E3)",
    "tiktok": "corte de 60-90s com o termo de busca falado nos 3 primeiros segundos",
    "youtube": "short com 'vídeo relacionado' apontando para o vídeo longo",
    "linkedin": "texto publicado à mão (fora do Metricool por decisão do Diogo)",
}


@dataclass
class Peca:
    data_hora: str
    rede: str
    pilar: str
    formato: str
    instagram_tipo: str | None = None


def _mais(hora: time, minutos: int) -> time:
    return (datetime.combine(date.min, hora) + timedelta(minutes=minutos)).time()


def grade_semana(segunda: date) -> list[Peca]:
    """Gera as peças de segunda a sexta a partir da segunda-feira informada."""
    if segunda.weekday() != 0:
        raise ValueError("A grade começa numa segunda-feira")
    pecas: list[Peca] = []
    for i, (quadro, hora) in QUADRO_DO_DIA.items():
        dia = segunda + timedelta(days=i)
        slots = [
            (dia, hora, "instagram", "REEL"),
            (dia, _mais(hora, 30), "tiktok", None),
            (dia, time(16, 0), "youtube", None),
        ]
        if i in (2, 3):
            slots.append((dia, time(18, 0), "instagram_trial", "TRIAL_REEL"))
        if quadro != "Doutor Di":
            slots.append((dia, time(8, 0), "linkedin", None))
        for d, h, rede, tipo in slots:
            formato = FORMATOS[rede]
            if rede == "tiktok" and quadro == "Radar Cooperativo":
                formato = "vídeo inteiro (o Radar já tem 60-90s)"
            pecas.append(Peca(datetime.combine(d, h).isoformat(), rede.split("_")[0], quadro, formato, tipo))
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
