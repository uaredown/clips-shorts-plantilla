"""Explora un tramo de un vídeo/VOD SIN bajar el vídeo: solo audio → transcripción con tiempos absolutos + segundos más fuertes
(gritos/risas = reacción). Sirve para afinar un pico del heatmap (momentos_youtube.py) antes de descargar el clip en 1080p.
Uso: python explorar_tramo.py <url | archivo local> <desde hh:mm:ss> <hasta hh:mm:ss> [--modelo small]
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
import numpy as np  # noqa: E402
from faster_whisper import WhisperModel  # noqa: E402


def seg(t):
    s = 0.0
    for p in str(t).split(":"):
        s = s * 60 + float(p)
    return s


def hms(s):
    s = int(s)
    return f"{s // 3600}:{s // 60 % 60:02d}:{s % 60:02d}"


url, desde, hasta = sys.argv[1], sys.argv[2], sys.argv[3]
modelo = sys.argv[sys.argv.index("--modelo") + 1] if "--modelo" in sys.argv else "small"
t0 = seg(desde)
with tempfile.TemporaryDirectory() as tmp:
    base = Path(tmp) / "a"
    cmd = ["yt-dlp", "-q", "--no-progress", "-f", "ba/b", "--download-sections", f"*{desde}-{hasta}",
           "-o", str(base) + ".%(ext)s", url]
    if "youtu" in url:
        cmd[1:1] = ["--js-runtimes", "node"]
    if Path(url).exists():  # archivo local (p. ej. fuente.mp4 de un directo grabado): cortar el tramo sin descargar
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t0), "-to", str(seg(hasta)), "-i", url, "-vn",
                        str(base) + ".wav"])
    else:
        subprocess.run(cmd, capture_output=True)
    f = next(Path(tmp).glob("a.*"), None)
    if not f:
        sys.exit("no se pudo bajar el audio del tramo")
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    rms = [float(np.sqrt(np.mean(x[i:i + 16000] ** 2))) for i in range(0, len(x) - 16000, 16000)]
    m = WhisperModel(modelo, device="cpu", compute_type="int8")
    segs, info = m.transcribe(str(f), vad_filter=True, beam_size=5)
    for s_ in segs:
        print(f"{hms(t0 + s_.start)}-{hms(t0 + s_.end)} {s_.text.strip()[:150]}")
top = sorted(range(len(rms)), key=lambda i: -rms[i])[:6]
media = np.mean(rms) or 1
print("Más fuerte (gritos/risas):", " · ".join(f"{hms(t0 + i)} x{rms[i] / media:.1f}" for i in sorted(top)))
