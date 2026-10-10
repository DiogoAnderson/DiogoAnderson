"""Empacota uma ideia (ou a transcrição de um vídeo) para as quatro redes, usando o Claude.

O vídeo é o mesmo; a embalagem muda por rede, porque cada algoritmo lê sinais diferentes:
- Instagram: gancho nos 3 primeiros segundos + motivo para mandar por DM + palavra-chave de comentário
- TikTok: palavra de busca dita em voz alta e escrita na legenda (o TikTok trata a legenda como SEO)
- YouTube Shorts: título que funciona como busca e aponta para o vídeo longo
- LinkedIn: texto nativo até 1.500 caracteres, sem link no corpo

Requer: pip install anthropic  e  ANTHROPIC_API_KEY (ou `ant auth login`).
"""

from __future__ import annotations

import json
import sys

import anthropic

MODELO = "claude-opus-5-5"

LIMITES = {"legenda_instagram": 800, "post_linkedin": 1500, "legenda_tiktok": 2200, "titulo_short": 100}

SISTEMA = """Você escreve para Diogo Anderson Angioleti: mais de 20 anos no cooperativismo financeiro,
consultor (marca PP&P — Pessoas, Propósito & Prosperidade), professor, palestrante de educação financeira,
RH e governança. Voz calorosa e direta, fala com "você", liga tema técnico a uma cena do dia a dia,
emoção com número junto. Sempre no masculino ao se referir a ele.

Regras de texto (não negociáveis):
- Comece pelo fato, cena ou número. Nada de "Em um mundo cada vez mais...", "Vamos falar sobre...".
- Proibido: "Não é sobre X, é sobre Y"; listas negativas em trio; frases de efeito isoladas ("Simples assim.");
  "Vale destacar"; "No fim do dia"; kintsugi, fênix, iceberg, zona de conforto, lagarta/borboleta.
- Uma analogia do cotidiano que deixe o conceito mais claro.
- Não invente número, pesquisa ou citação. Se a ideia não trouxe o dado, escreva sem o dado.
- Português correto: "houve", "faz dois anos", "em vez de", "a maioria acredita", sem gerundismo.

Regras de algoritmo:
- O gancho é a primeira frase falada E o texto na tela no segundo zero. Até 12 palavras. Precisa abrir uma
  pergunta que só se fecha assistindo. Dê variações de tipos diferentes (número, conflito, pergunta, cena).
- Toda peça precisa de um motivo concreto para alguém mandar para outra pessoa ("manda para quem...").
- A palavra-chave de comentário é uma palavra única em maiúsculas que dispara a resposta automática no
  Instagram (ManyChat). Ela entrega algo útil e real que o autor tenha (checklist, planilha, episódio completo).
- TikTok: inclua 3 a 5 termos que as pessoas digitam na busca, em linguagem de busca, não hashtags de vaidade.
- LinkedIn: sem link no corpo; feche com uma pergunta que só faça sentido para este tema."""

ESQUEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["ganchos", "roteiro_45s", "legenda_instagram", "palavra_comentario", "entrega_comentario",
                 "motivo_para_enviar", "legenda_tiktok", "termos_busca_tiktok", "titulo_short", "post_linkedin"],
    "properties": {
        "ganchos": {"type": "array", "items": {"type": "string"}},
        "roteiro_45s": {"type": "string"},
        "legenda_instagram": {"type": "string"},
        "palavra_comentario": {"type": "string"},
        "entrega_comentario": {"type": "string"},
        "motivo_para_enviar": {"type": "string"},
        "legenda_tiktok": {"type": "string"},
        "termos_busca_tiktok": {"type": "array", "items": {"type": "string"}},
        "titulo_short": {"type": "string"},
        "post_linkedin": {"type": "string"},
    },
}


def estouros(pacote: dict) -> dict[str, int]:
    """Campos que passaram do limite da rede, com o tamanho real (contado, não estimado)."""
    return {campo: len(pacote[campo]) for campo, limite in LIMITES.items() if len(pacote.get(campo, "")) > limite}


def _pedir(client: anthropic.Anthropic, mensagens: list[dict]) -> tuple[dict, dict]:
    resposta = client.beta.messages.create(
        model=MODELO,
        max_tokens=16000,
        system=SISTEMA,
        messages=mensagens,
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": ESQUEMA}},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if resposta.stop_reason == "refusal":
        raise RuntimeError("O modelo recusou o pedido; reformule a ideia.")
    texto = next(b.text for b in resposta.content if b.type == "text")
    return json.loads(texto), {"role": "assistant", "content": resposta.content}


def empacotar(ideia: str, pilar: str = "", client: anthropic.Anthropic | None = None) -> dict:
    client = client or anthropic.Anthropic()
    mensagens = [{"role": "user", "content": f"Pilar do dia: {pilar or 'livre'}\n\nIdeia ou transcrição:\n{ideia}\n\n"
                                             "Gere 5 ganchos de tipos diferentes e o pacote completo."}]
    pacote, turno = _pedir(client, mensagens)
    excesso = estouros(pacote)
    if excesso:
        mensagens += [turno, {"role": "user", "content":
                              "Estes campos passaram do limite (caracteres contados): "
                              + ", ".join(f"{c} = {n}, máximo {LIMITES[c]}" for c, n in excesso.items())
                              + ". Corte detalhe, não a voz, e devolva o pacote inteiro."}]
        pacote, _ = _pedir(client, mensagens)
    return pacote


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('uso: python -m crescimento.ganchos "ideia ou caminho/para/transcricao.txt" [pilar]')
    entrada = sys.argv[1]
    try:
        with open(entrada, encoding="utf-8") as f:
            entrada = f.read()
    except OSError:
        pass
    resultado = empacotar(entrada, sys.argv[2] if len(sys.argv) > 2 else "")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    for campo, limite in LIMITES.items():
        print(f"# {campo}: {len(resultado[campo])}/{limite} caracteres", file=sys.stderr)
