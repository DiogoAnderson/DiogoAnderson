"""Vídeo para as redes: conferir, converter, transcrever, cortar e legendar.

Tudo gratuito (ffmpeg + faster-whisper rodando na máquina). Usado pela Central, pelas
tarefas do Claude e pelo GitHub Actions.

    python -m central.video conferir VIDEO
    python -m central.video transcrever VIDEO --saida legenda.srt
    python -m central.video sugerir VIDEO            # trechos com mais cara de gancho
    python -m central.video cortar VIDEO --inicio 151 --fim 237 --saida corte.mp4 [--legenda]

Limites que derrubaram posts em 13/10/2026: o TikTok exige média de 23 a 60 quadros por
segundo e o Instagram recusa vídeo acima de cerca de 300 MB. A conversão sai sempre em
H.264, 30 fps constantes, 1080x1920, abaixo de 100 MB (cabe no GitHub).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FONTES = RAIZ / "marca" / "fontes"
LIMITE_INSTAGRAM_MB = 300
LIMITE_REPO_MB = 95
FPS_MIN, FPS_MAX = 23, 60


@dataclass
class Ficha:
    duracao: float
    largura: int
    altura: int
    fps_medio: float
    codec: str
    tamanho_mb: float

    def problemas(self) -> list[str]:
        p = []
        if not FPS_MIN <= self.fps_medio <= FPS_MAX:
            p.append(f"{self.fps_medio:.1f} quadros por segundo (TikTok exige de {FPS_MIN} a {FPS_MAX})")
        if self.tamanho_mb > LIMITE_INSTAGRAM_MB:
            p.append(f"{self.tamanho_mb:.0f} MB (Instagram aceita até cerca de {LIMITE_INSTAGRAM_MB} MB)")
        if self.codec not in ("h264",):
            p.append(f"codec {self.codec} (o mais aceito é H.264)")
        return p


def baixar(origem: str, destino_dir: Path) -> Path:
    """Aceita caminho local, link do Drive (id ou URL) ou URL pública."""
    if Path(origem).exists():
        return Path(origem)
    if "drive.google.com" in origem or (len(origem) in range(25, 45) and "/" not in origem):
        fid = origem.split("/d/")[1].split("/")[0] if "/d/" in origem else origem.split("id=")[-1].split("&")[0]
        origem = f"https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t"
    destino = destino_dir / "entrada.mp4"
    urllib.request.urlretrieve(origem, destino)
    return destino


def conferir(video: Path) -> Ficha:
    saida = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,avg_frame_rate,codec_name:format=duration,size", "-of", "json", str(video)],
        capture_output=True, text=True, check=True).stdout
    d = json.loads(saida)
    s, f = d["streams"][0], d["format"]
    num, den = (s.get("avg_frame_rate") or "0/1").split("/")
    fps = float(num) / float(den) if float(den) else 0.0
    return Ficha(float(f["duration"]), int(s["width"]), int(s["height"]), fps, s["codec_name"],
                 int(f["size"]) / 1e6)


def transcrever(video: Path, inicio: float = 0, fim: float | None = None, palavras: bool = True):
    """Transcreve em português. Devolve segmentos com palavras e tempos relativos a `inicio`."""
    import numpy as np
    from faster_whisper import WhisperModel

    cmd = ["ffmpeg", "-v", "error", "-ss", str(inicio)]
    if fim is not None:
        cmd += ["-to", str(fim)]
    cmd += ["-i", str(video), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"]
    # Passar o áudio já decodificado evita a falha do decodificador interno (av) com alguns arquivos.
    bruto = subprocess.run(cmd, capture_output=True, check=True).stdout
    audio = np.frombuffer(bruto, dtype=np.int16).astype(np.float32) / 32768
    modelo = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = modelo.transcribe(audio, language="pt", vad_filter=True, word_timestamps=palavras)
    return list(segs)


def _carimbo_srt(x: float) -> str:
    return f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{x % 60:06.3f}".replace(".", ",")


def para_srt(segs) -> str:
    return "".join(f"{i}\n{_carimbo_srt(s.start)} --> {_carimbo_srt(s.end)}\n{s.text.strip()}\n\n"
                   for i, s in enumerate(segs, 1))


def _carimbo_ass(x: float) -> str:
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"


def legenda_ass(segs, palavras_por_bloco: int = 3) -> str:
    """Legenda em blocos curtos, com a palavra falada em amarelo (estilo dos Reels que retêm)."""
    cabecalho = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Marca,Montserrat Black,62,&H00FFFFFF,&H00FFFFFF,&H00101010,&H64000000,1,0,0,0,100,100,0,0,1,7,3,2,80,80,520,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    linhas = []
    todas = [w for s in segs for w in (s.words or [])]
    for i in range(0, len(todas), palavras_por_bloco):
        bloco = todas[i:i + palavras_por_bloco]
        for j, w in enumerate(bloco):
            fim = bloco[j + 1].start if j + 1 < len(bloco) else w.end
            texto = " ".join(
                ("{\\c&H11C3F2&}" + x.word.strip().upper() + "{\\c&HFFFFFF&}") if k == j else x.word.strip().upper()
                for k, x in enumerate(bloco))
            linhas.append(f"Dialogue: 0,{_carimbo_ass(w.start)},{_carimbo_ass(fim)},Marca,,0,0,0,,{texto}")
    return cabecalho + "\n".join(linhas) + "\n"


def cortar(video: Path, saida: Path, inicio: float = 0, fim: float | None = None,
           legenda: bool = False, crf: int = 23) -> Ficha:
    """Corta, enquadra em 9:16, fixa 30 fps e, se pedido, queima a legenda animada."""
    filtros = ["scale=1080:1920:force_original_aspect_ratio=increase", "crop=1080:1920", "fps=30"]
    with tempfile.TemporaryDirectory() as tmp:
        if legenda:
            ass = Path(tmp) / "legenda.ass"
            ass.write_text(legenda_ass(transcrever(video, inicio, fim)), encoding="utf-8")
            filtros.append(f"ass={ass}:fontsdir={FONTES}")
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(inicio)]
        if fim is not None:
            cmd += ["-to", str(fim)]
        cmd += ["-i", str(video), "-vf", ",".join(filtros), "-c:v", "libx264", "-preset", "medium",
                "-crf", str(crf), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                "-movflags", "+faststart", str(saida)]
        subprocess.run(cmd, check=True)
    ficha = conferir(saida)
    if ficha.tamanho_mb > LIMITE_REPO_MB and crf < 32:
        return cortar(video, saida, inicio, fim, legenda, crf + 3)
    return ficha


def preparar(video: Path, saida: Path) -> Ficha:
    """Vídeo inteiro que não passou na conferência: converte sem cortar nem legendar."""
    return cortar(video, saida, legenda=False)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="python -m central.video")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nome in ("conferir", "transcrever", "sugerir", "cortar", "preparar"):
        p = sub.add_parser(nome)
        p.add_argument("video")
        if nome in ("transcrever", "cortar", "preparar"):
            p.add_argument("--saida", required=nome != "transcrever")
        if nome == "cortar":
            p.add_argument("--inicio", type=float, default=0)
            p.add_argument("--fim", type=float)
            p.add_argument("--legenda", action="store_true",
                           help="queima legenda animada (use só em vídeo que ainda não tem legenda)")
    a = ap.parse_args(argv)
    with tempfile.TemporaryDirectory() as tmp:
        video = baixar(a.video, Path(tmp))
        if a.cmd == "conferir":
            f = conferir(video)
            print(json.dumps({**f.__dict__, "problemas": f.problemas()}, ensure_ascii=False, indent=2))
        elif a.cmd == "transcrever":
            srt = para_srt(transcrever(video, palavras=False))
            Path(a.saida).write_text(srt, encoding="utf-8") if a.saida else sys.stdout.write(srt)
        elif a.cmd == "sugerir":
            from crescimento.cortes import ler_srt, sugerir_cortes
            for c in sugerir_cortes(ler_srt(para_srt(transcrever(video, palavras=False))), 45, 90, 5):
                print(json.dumps({"inicio": round(c.inicio, 1), "fim": round(c.fim, 1), "nota": c.nota,
                                  "gancho": c.gancho}, ensure_ascii=False))
        elif a.cmd == "cortar":
            f = cortar(video, Path(a.saida), a.inicio, a.fim, a.legenda)
            print(json.dumps(f.__dict__, ensure_ascii=False))
        elif a.cmd == "preparar":
            print(json.dumps(preparar(video, Path(a.saida)).__dict__, ensure_ascii=False))


if __name__ == "__main__":
    main()
