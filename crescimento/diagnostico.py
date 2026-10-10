"""Diagnóstico de algoritmo a partir dos dados exportados do Metricool.

Lê os CSVs em crescimento/dados/ e responde três perguntas:
1. O que segura o vídeo nos primeiros 3 segundos (taxa_3s) e quanto isso pesa nas views?
2. Que conteúdo gera envio por DM / compartilhamento (o sinal mais forte para alcançar não seguidores)?
3. Que hábitos de publicação (horário, duração, tema fora do nicho) estão travando o alcance?
"""

from __future__ import annotations

import csv
import statistics
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

DADOS = Path(__file__).parent / "dados"

# Palavras-chave por pilar. A ordem importa: o primeiro pilar que bater vence.
PILARES = {
    "evento/bastidor": ["concred", "conarh", "hj conference", "sipat", "fotos", "abertura", "delegação",
                        "workshop", "palestra", "mentoria", "convite", "autógrafos", "lançamento", "dia do"],
    "pessoal/lifestyle": ["mãe", "mamãe", "rainha", "aniversário", "mood", "tattoo", "egito", "china",
                          "trip", "pele", "skincare", "os mano", "luta boa", "sem legenda", "rei charles"],
    "notícia/radar": ["radar", "prévia da inflação", "stf", "reforma tributária", "baniu", "proíbe", "governo"],
    "educação financeira": ["dinheiro", "bets", "apostar", "golpe", "dívida", "boleto", "cartão", "gasta",
                            "budgeting", "13º", "dr di", "ep.", "financeir", "pix", "gastador", "criaturinha",
                            "recursos limitados", "remuneração"],
    "RH/governança/liderança": ["líder", "lideran", "conselho", "geração z", "gestor", "nr-1", "engajamento",
                                "associadas", "jovens", "presidente", "superintendente", "cooperativismo"],
    "reflexão/comportamento": ["reflex", "rancor", "perdão", "sentido", "carrega", "sorte", "ouvir", "regra de",
                               "elevador", "ódio", "verbo ser", "serendipidade", "continue", "amor", "vamos viver"],
}


@dataclass
class Post:
    publicado_em: datetime
    views: float
    legenda: str
    extras: dict

    @property
    def hora(self) -> int:
        return self.publicado_em.hour

    @property
    def pilar(self) -> str:
        texto = self.legenda.lower()
        for pilar, chaves in PILARES.items():
            if any(c in texto for c in chaves):
                return pilar
        return "outros"


def _ler_csv(caminho: Path) -> list[Post]:
    posts = []
    with caminho.open(encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            extras = {k: float(v) for k, v in linha.items()
                      if k not in ("publicado_em", "views", "legenda") and v not in ("", None)}
            posts.append(Post(datetime.strptime(linha["publicado_em"], "%Y-%m-%d %H:%M"),
                              float(linha["views"]), linha["legenda"], extras))
    return posts


def carregar(rede: str) -> list[Post]:
    padrao = {"instagram": "ig_reels_*.csv", "tiktok": "tiktok_videos_*.csv"}[rede]
    arquivos = sorted(DADOS.glob(padrao))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum CSV {padrao} em {DADOS}")
    return _ler_csv(arquivos[-1])


def mediana(valores) -> float:
    valores = list(valores)
    return statistics.median(valores) if valores else 0.0


def faixa_horaria(hora: int) -> str:
    if hora < 6:
        return "madrugada (0h-5h)"
    if hora < 12:
        return "manhã (6h-11h)"
    if hora < 18:
        return "tarde (12h-17h)"
    return "noite (18h-23h)"


def agrupar(posts: list[Post], chave) -> dict[str, list[Post]]:
    grupos: dict[str, list[Post]] = {}
    for p in posts:
        grupos.setdefault(chave(p), []).append(p)
    return grupos


def correlacao(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 3:
        return 0.0
    return statistics.correlation(xs, ys)


def sem_outliers(posts: list[Post], limite: float = 5000) -> list[Post]:
    """Remove virais pontuais e posts impulsionados, que distorcem a mediana orgânica."""
    return [p for p in posts if p.views < limite]


def analisar_instagram(posts: list[Post]) -> dict:
    taxa = [p.extras["taxa_3s"] for p in posts]
    views = [p.views for p in posts]
    fortes = [p for p in posts if p.extras["taxa_3s"] >= 45]
    fracos = [p for p in posts if p.extras["taxa_3s"] < 35]
    envios = sorted(posts, key=lambda p: p.extras["shares"], reverse=True)
    return {
        "total": len(posts),
        "mediana_views": mediana(views),
        "mediana_taxa_3s": mediana(taxa),
        "correl_taxa3s_views": correlacao(taxa, views),
        "mediana_views_gancho_forte": mediana(p.views for p in fortes),
        "mediana_views_gancho_fraco": mediana(p.views for p in fracos),
        "qtd_gancho_forte": len(fortes),
        "posts_sem_nenhum_envio": sum(1 for p in posts if p.extras["shares"] == 0),
        "top_envios": [(p.legenda, int(p.extras["shares"]), int(p.views)) for p in envios[:6]],
        "por_horario": {k: (len(v), mediana(p.views for p in v))
                        for k, v in sorted(agrupar(posts, lambda p: faixa_horaria(p.hora)).items())},
        "por_pilar": {k: (len(v), mediana(p.views for p in v), sum(p.extras["shares"] for p in v))
                      for k, v in sorted(agrupar(posts, lambda p: p.pilar).items())},
    }


def faixa_duracao(segundos: float) -> str:
    if segundos <= 30:
        return "até 30s"
    if segundos <= 90:
        return "31-90s"
    if segundos <= 180:
        return "91-180s"
    return "acima de 3 min"


def analisar_tiktok(posts: list[Post]) -> dict:
    organicos = sem_outliers(posts)
    return {
        "total": len(posts),
        "mediana_views_organica": mediana(p.views for p in organicos),
        "virais_ou_impulsionados": [(p.legenda, int(p.views)) for p in posts if p.views >= 5000],
        "por_duracao": {k: (len(v), mediana(p.views for p in v))
                        for k, v in agrupar(organicos, lambda p: faixa_duracao(p.extras["duracao_s"])).items()},
        "por_pilar": {k: (len(v), mediana(p.views for p in v))
                      for k, v in sorted(agrupar(organicos, lambda p: p.pilar).items())},
        "fora_do_nicho_pct": 100 * sum(1 for p in organicos if p.pilar in ("pessoal/lifestyle", "evento/bastidor"))
        / max(len(organicos), 1),
    }


def relatorio() -> str:
    ig = analisar_instagram(carregar("instagram"))
    tk = analisar_tiktok(carregar("tiktok"))
    linhas = [
        "# Diagnóstico de algoritmo",
        "",
        "## Instagram (Reels)",
        f"- Reels analisados: {ig['total']} | mediana de views: {ig['mediana_views']:.0f}",
        f"- Mediana da taxa de 3 segundos: {ig['mediana_taxa_3s']:.1f}% "
        f"(correlação com views: {ig['correl_taxa3s_views']:.2f})",
        f"- Gancho forte (>=45% passam dos 3s): {ig['qtd_gancho_forte']} reels, mediana "
        f"{ig['mediana_views_gancho_forte']:.0f} views; gancho fraco (<35%): mediana "
        f"{ig['mediana_views_gancho_fraco']:.0f} views",
        f"- Reels com zero envios/compartilhamentos: {ig['posts_sem_nenhum_envio']} de {ig['total']}",
        "",
        "### O que mais gerou envios (o sinal que leva a não seguidores)",
        *[f"- {leg}: {s} envios, {v} views" for leg, s, v in ig["top_envios"]],
        "",
        "### Por horário de publicação",
        *[f"- {k}: {n} reels, mediana {m:.0f} views" for k, (n, m) in ig["por_horario"].items()],
        "",
        "### Por pilar de conteúdo",
        *[f"- {k}: {n} reels, mediana {m:.0f} views, {s:.0f} envios no total"
          for k, (n, m, s) in ig["por_pilar"].items()],
        "",
        "## TikTok",
        f"- Vídeos analisados: {tk['total']} | mediana orgânica: {tk['mediana_views_organica']:.0f} views",
        f"- Conteúdo fora do nicho (pessoal, bastidor): {tk['fora_do_nicho_pct']:.0f}% dos vídeos orgânicos",
        "",
        "### Por duração",
        *[f"- {k}: {n} vídeos, mediana {m:.0f} views" for k, (n, m) in tk["por_duracao"].items()],
        "",
        "### Picos (viral ou impulsionado — fora da mediana)",
        *[f"- {leg}: {v} views" for leg, v in tk["virais_ou_impulsionados"]],
    ]
    return "\n".join(linhas) + "\n"


if __name__ == "__main__":
    print(relatorio())
