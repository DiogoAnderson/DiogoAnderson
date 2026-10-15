"""Gera as peças visuais da marca (capa de Reel e lâmina de carrossel) a partir dos modelos HTML.

Os modelos ficam em marca/modelos/ e usam a identidade da Angioletti (marinho, dourado,
EB Garamond e Montserrat). A foto é sempre do Diogo: a regra do Master Growth proíbe
banco de imagens e rosto gerado por IA. O Chromium (via Playwright) abre o HTML e fotografa a página
no tamanho exato da rede.

Uso:
    python -m crescimento.pecas capa --foto foto.jpg --selo "Educação Financeira" \
        --gancho "O 13º já tem dono?" --destaque "tem dono?" --apoio "Antes de cair, ele já foi gasto" \
        --saida capa.png
    python -m crescimento.pecas lamina --selo "Radar Cooperativo" --num 1/6 \
        --titulo "Três notícias que mexem no seu bolso" --texto "..." --saida lamina1.png
"""

from __future__ import annotations

import argparse
import glob
import shutil
from pathlib import Path
from urllib.parse import quote, urlencode

RAIZ = Path(__file__).resolve().parent.parent
MODELOS = RAIZ / "marca" / "modelos"
TAMANHOS = {"capa": (1080, 1920, "capa-reel.html"), "lamina": (1080, 1350, "lamina-carrossel.html"),
            "mentor": (1280, 720, "thumb-mentor-sincerao.html"),
            "doutordi": (1080, 1920, "capa-doutor-di.html")}


def achar_chromium() -> str | None:
    """Usa o Chromium já instalado no ambiente (sem baixar outro)."""
    candidatos = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
    if candidatos:
        return candidatos[-1]
    for nome in ("chromium", "chromium-browser", "google-chrome"):
        if caminho := shutil.which(nome):
            return caminho
    return None


def montar_url(tipo: str, campos: dict[str, str]) -> str:
    _, _, arquivo = TAMANHOS[tipo]
    campos = {k: v for k, v in campos.items() if v}
    for imagem in ("foto", "fundo"):
        if imagem in campos and "://" not in campos[imagem]:
            campos[imagem] = Path(campos[imagem]).resolve().as_uri()
    return (MODELOS / arquivo).as_uri() + "?" + urlencode(campos, quote_via=quote)


def gerar(tipo: str, campos: dict[str, str], saida: str) -> Path:
    from playwright.sync_api import sync_playwright

    largura, altura, _ = TAMANHOS[tipo]
    destino = Path(saida).resolve()
    with sync_playwright() as pw:
        navegador = pw.chromium.launch(executable_path=achar_chromium(),
                                       args=["--allow-file-access-from-files"])
        pagina = navegador.new_page(viewport={"width": largura, "height": altura})
        pagina.goto(montar_url(tipo, campos))
        pagina.wait_for_load_state("networkidle")
        pagina.evaluate("document.fonts.ready")
        pagina.screenshot(path=str(destino), clip={"x": 0, "y": 0, "width": largura, "height": altura})
        navegador.close()
    return destino


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tipo", choices=TAMANHOS)
    for campo in ("foto", "fundo", "foco", "selo", "gancho", "destaque", "apoio", "num", "titulo", "texto", "parte",
                  "ep", "chamada", "doenca1", "doenca2", "apoio1", "apoio2", "balao", "topo1", "topo2"):
        ap.add_argument(f"--{campo}")
    ap.add_argument("--saida", required=True)
    args = vars(ap.parse_args())
    tipo, saida = args.pop("tipo"), args.pop("saida")
    print(gerar(tipo, args, saida))


if __name__ == "__main__":
    main()
