"""Publicação direta no Instagram pela API oficial da Meta (Instagram Graph API). Gratuita.

Credenciais (nunca no código): variáveis de ambiente IG_TOKEN (token de página, que não
expira) e IG_USER_ID (id da conta profissional do Instagram). No GitHub ficam em
Settings → Secrets and variables → Actions. Sem elas, tudo roda em modo ensaio e só
imprime o que faria.

Formatos: reel, story (imagem ou vídeo), post (imagem) e carrossel (2 a 10 imagens).
Vídeo sobe direto do arquivo local (upload retomável), então não precisa de link público.
"""

from __future__ import annotations

import json
import mimetypes
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

VERSAO = "v21.0"
GRAPH = f"https://graph.facebook.com/{VERSAO}"
RUPLOAD = f"https://rupload.facebook.com/ig-api-upload/{VERSAO}"


class ErroInstagram(RuntimeError):
    pass


def configurado() -> bool:
    return bool(os.environ.get("IG_TOKEN") and os.environ.get("IG_USER_ID"))


def _chamar(metodo: str, url: str, dados: dict | None = None, cabecalhos: dict | None = None,
            corpo: bytes | None = None) -> dict:
    token = os.environ["IG_TOKEN"]
    if dados is not None:
        dados = {**dados, "access_token": token}
        corpo = urllib.parse.urlencode(dados).encode()
    elif "access_token" not in url and cabecalhos is None:
        url += ("&" if "?" in url else "?") + "access_token=" + token
    req = urllib.request.Request(url, data=corpo, method=metodo, headers=cabecalhos or {})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        detalhe = e.read().decode(errors="replace")
        try:
            detalhe = json.loads(detalhe)["error"]["message"]
        except Exception:
            pass
        raise ErroInstagram(f"{e.code}: {detalhe}") from None


def conta() -> dict:
    """Confere o token: devolve o @ e o número de seguidores."""
    return _chamar("GET", f"{GRAPH}/{os.environ['IG_USER_ID']}?fields=username,followers_count,media_count")


def cota() -> dict:
    """Quantas publicações a conta ainda pode fazer nas últimas 24 h (limite da Meta: 100)."""
    r = _chamar("GET", f"{GRAPH}/{os.environ['IG_USER_ID']}/content_publishing_limit?fields=quota_usage,config")
    return (r.get("data") or [{}])[0]


def _container(campos: dict) -> str:
    return _chamar("POST", f"{GRAPH}/{os.environ['IG_USER_ID']}/media", campos)["id"]


def _enviar_video(container: str, arquivo: Path) -> None:
    dados = arquivo.read_bytes()
    _chamar("POST", f"{RUPLOAD}/{container}", cabecalhos={
        "Authorization": f"OAuth {os.environ['IG_TOKEN']}", "offset": "0", "file_size": str(len(dados)),
        "Content-Type": "application/octet-stream"}, corpo=dados)


def _esperar(container: str, limite_s: int = 900) -> None:
    inicio = time.time()
    while time.time() - inicio < limite_s:
        st = _chamar("GET", f"{GRAPH}/{container}?fields=status_code,status")
        if st.get("status_code") == "FINISHED":
            return
        if st.get("status_code") in ("ERROR", "EXPIRED"):
            raise ErroInstagram(f"o Instagram recusou o vídeo: {st.get('status')}")
        time.sleep(10)
    raise ErroInstagram("o Instagram demorou mais de 15 minutos para processar o vídeo")


def _publicar(container: str) -> str:
    return _chamar("POST", f"{GRAPH}/{os.environ['IG_USER_ID']}/media_publish", {"creation_id": container})["id"]


def _eh_video(caminho: str) -> bool:
    return (mimetypes.guess_type(caminho)[0] or "").startswith("video")


def publicar(tipo: str, midias: list[str], legenda: str = "", primeiro_comentario: str = "",
             capa_url: str | None = None, compartilhar_no_feed: bool = True) -> dict:
    """`midias`: arquivos locais (vídeos) ou URLs públicas (imagens). Devolve id e link do post."""
    if tipo == "reel":
        c = _container({"media_type": "REELS", "upload_type": "resumable", "caption": legenda,
                        "share_to_feed": str(compartilhar_no_feed).lower(), **({"cover_url": capa_url} if capa_url else {})})
        _enviar_video(c, Path(midias[0]))
    elif tipo == "story":
        if _eh_video(midias[0]):
            c = _container({"media_type": "STORIES", "upload_type": "resumable"})
            _enviar_video(c, Path(midias[0]))
        else:
            c = _container({"media_type": "STORIES", "image_url": midias[0]})
    elif tipo == "post":
        c = _container({"image_url": midias[0], "caption": legenda})
    elif tipo == "carrossel":
        filhos = [_container({"image_url": m, "is_carousel_item": "true"}) for m in midias[:10]]
        c = _container({"media_type": "CAROUSEL", "children": ",".join(filhos), "caption": legenda})
    else:
        raise ErroInstagram(f"tipo desconhecido: {tipo}")
    _esperar(c)
    mid = _publicar(c)
    link = _chamar("GET", f"{GRAPH}/{mid}?fields=permalink").get("permalink", "")
    if primeiro_comentario and tipo != "story":
        try:
            _chamar("POST", f"{GRAPH}/{mid}/comments", {"message": primeiro_comentario})
        except ErroInstagram as e:
            return {"id": mid, "link": link, "aviso": f"post publicado, mas o primeiro comentário falhou: {e}"}
    return {"id": mid, "link": link}


if __name__ == "__main__":
    if not configurado():
        raise SystemExit("Faltam IG_TOKEN e IG_USER_ID (veja central/COMO-LIGAR-O-INSTAGRAM.md).")
    print(json.dumps({"conta": conta(), "cota_24h": cota()}, ensure_ascii=False, indent=2))
