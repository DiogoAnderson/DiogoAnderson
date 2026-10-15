"""Fila de publicação própria (hoje: Instagram direto, sem gastar a cota do Metricool).

Cada publicação é um arquivo JSON em central/fila/. Quem escreve: a Central (pelo Claude),
as tarefas do Claude e o pacote de terça. Quem publica: o GitHub Actions, a cada 15 minutos.

    {
      "id": "2026-10-20-mentor-6-reel",
      "rede": "instagram",
      "tipo": "reel" | "story" | "post" | "carrossel",
      "quando": "2026-10-20T10:00:00-03:00",
      "midias": ["midia/2026-10/x.mp4" ou "https://..." ou "drive:<id>"],
      "capa": "https://... (opcional, só reel)",
      "legenda": "...",
      "primeiro_comentario": "...",
      "cortar": {"inicio": 151, "fim": 237, "legenda": false},   (opcional)
      "status": "agendado" | "rascunho" | "publicado" | "erro",
      "resultado": {"link": "...", "quando": "...", "erro": "..."}
    }

    python -m central.fila listar
    python -m central.fila publicar [--ensaio]     # publica o que já venceu
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import tempfile
from pathlib import Path

from central import instagram, video

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "central" / "fila"
RAW = "https://raw.githubusercontent.com/DiogoAnderson/DiogoAnderson/ccr-efddba0a-tar1r3/"
FUSO = dt.timezone(dt.timedelta(hours=-3))


def itens() -> list[tuple[Path, dict]]:
    return sorted(((p, json.loads(p.read_text(encoding="utf-8"))) for p in PASTA.glob("*.json")),
                  key=lambda x: x[1].get("quando", ""))


def salvar(caminho: Path, item: dict) -> None:
    caminho.write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def vencidos(agora: dt.datetime | None = None) -> list[tuple[Path, dict]]:
    agora = agora or dt.datetime.now(FUSO)
    return [(p, i) for p, i in itens()
            if i.get("status") == "agendado" and dt.datetime.fromisoformat(i["quando"]) <= agora]


def _midia_local(origem: str, tmp: Path, n: int) -> Path:
    if origem.startswith("drive:"):
        origem = origem[6:]
    if (RAIZ / origem).exists():
        return RAIZ / origem
    destino = tmp / f"m{n}"
    destino.mkdir()
    return video.baixar(origem, destino)


def _midia_url(origem: str) -> str:
    """Imagens precisam de URL pública: arquivo do repositório vira link raw."""
    if origem.startswith(("http://", "https://")):
        return origem
    if origem.startswith("drive:"):
        return f"https://drive.usercontent.google.com/download?id={origem[6:]}&export=download&confirm=t"
    return RAW + origem


def publicar_item(item: dict, ensaio: bool = False) -> dict:
    if item.get("rede") != "instagram":
        raise ValueError(f"rede ainda não suportada pela fila própria: {item.get('rede')}")
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        midias = []
        for n, m in enumerate(item["midias"]):
            if instagram._eh_video(m) or m.startswith("drive:"):
                arq = _midia_local(m, tmp, n)
                ficha = video.conferir(arq)
                corte = item.get("cortar")
                if corte or ficha.problemas():
                    saida = tmp / f"pronto{n}.mp4"
                    video.cortar(arq, saida, (corte or {}).get("inicio", 0), (corte or {}).get("fim"),
                                 (corte or {}).get("legenda", False))
                    arq = saida
                midias.append(str(arq))
            else:
                midias.append(_midia_url(m))
        if ensaio or not instagram.configurado():
            return {"ensaio": True, "midias": midias}
        return instagram.publicar(item["tipo"], midias, item.get("legenda", ""),
                                  item.get("primeiro_comentario", ""), item.get("capa"))


def publicar_vencidos(ensaio: bool = False) -> int:
    falhas = 0
    for caminho, item in vencidos():
        agora = dt.datetime.now(FUSO).isoformat(timespec="minutes")
        try:
            r = publicar_item(item, ensaio)
            if r.get("ensaio"):
                print(f"[ensaio] {item['id']}: {r}")
                continue
            item["status"], item["resultado"] = "publicado", {**r, "quando": agora}
            print(f"publicado {item['id']}: {r.get('link')}")
        except Exception as e:  # noqa: BLE001 — cada item falha sozinho, o resto segue
            falhas += 1
            item["status"], item["resultado"] = "erro", {"erro": str(e), "quando": agora}
            print(f"ERRO {item['id']}: {e}", file=sys.stderr)
        salvar(caminho, item)
    return falhas


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="python -m central.fila")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("listar")
    p = sub.add_parser("publicar")
    p.add_argument("--ensaio", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "listar":
        for _, i in itens():
            print(f"{i.get('quando', '')[:16]}  {i.get('status', ''):10} {i.get('rede')}/{i.get('tipo')}  {i['id']}")
    else:
        sys.exit(1 if publicar_vencidos(a.ensaio) else 0)


if __name__ == "__main__":
    main()
