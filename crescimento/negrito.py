"""Converte texto em negrito Unicode (sans-serif bold) para títulos de posts do LinkedIn,
que não aceita formatação. Acentos viram letra + acento combinado (NFD), que o LinkedIn exibe certo.

Uso: python -m crescimento.negrito "Título do post"
"""
import sys
import unicodedata


def negrito(texto: str) -> str:
    saida = []
    for c in unicodedata.normalize("NFD", texto):
        if "A" <= c <= "Z":
            saida.append(chr(0x1D5D4 + ord(c) - ord("A")))
        elif "a" <= c <= "z":
            saida.append(chr(0x1D5EE + ord(c) - ord("a")))
        elif "0" <= c <= "9":
            saida.append(chr(0x1D7EC + ord(c) - ord("0")))
        else:
            saida.append(c)
    return "".join(saida)


if __name__ == "__main__":
    print(negrito(" ".join(sys.argv[1:])))
