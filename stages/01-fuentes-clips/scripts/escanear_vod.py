"""Escanea un directo/VOD largo (sin heatmap) para encontrar momentos virales: baja SOLO el audio, lo transcribe entero
(faster-whisper "base", rápido) y puntúa cada frase por volumen (gritos/risas) + palabras de reacción del streamer.
Uso: python escanear_vod.py <url> [--modelo base] [--top 15] [--desde 0:48:40 --hasta 2:20:00]
     (en un VOD de un directo que sigue en vivo, poner SIEMPRE --desde/--hasta)
Salida en output/_vods/<id>/: transcripcion.tsv (inicio, fin, volumen relativo, texto) y candidatos.txt (los N mejores).
Después: explorar_tramo.py para afinar y descargar_clip.py --desde/--hasta para el clip en 1080p. El audio se borra al final.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
import numpy as np  # noqa: E402
from faster_whisper import WhisperModel  # noqa: E402

RAIZ = Path(__file__).resolve().parents[3]
REACCION = re.compile(r"\b(no way|what the|oh my god|bro+|chat|yo+|hell no|let'?s go+|w+hat|huh|nah+|help|run|why|"
                      r"stop|wait|oh no|bruh|crazy|insane|dead|ahh+|wow)\b", re.I)


def arg(n, d):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d


OFF = 0


def hms(s):
    s = int(s + OFF)
    return f"{s // 3600}:{s // 60 % 60:02d}:{s % 60:02d}"


url = sys.argv[1]
if "--desde" in sys.argv:
    OFF = sum(float(x) * k for x, k in zip(reversed(arg("--desde", "0").split(":")), (1, 60, 3600)))
info = json.loads(subprocess.run(["yt-dlp", "--js-runtimes", "node", "-J", "--no-playlist", url], capture_output=True,
                                 text=True, encoding="utf-8", errors="replace").stdout)
out = RAIZ / "output" / "_vods" / info["id"]
out.mkdir(parents=True, exist_ok=True)
audio = next(out.glob("audio.*"), None)
if not audio:
    cmd = ["yt-dlp", "-q", "--no-progress", "--js-runtimes", "node", "-f", "wa/ba/b", "-o", str(out / "audio.%(ext)s")]
    if "--desde" in sys.argv:  # tramo fijo (obligatorio en VODs de directos que siguen en marcha: si no, no acaba nunca)
        cmd += ["--download-sections", f"*{arg('--desde', '0')}-{arg('--hasta', '99:00:00')}"]
    subprocess.run(cmd + [url])
    audio = next(out.glob("audio.*"))
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(audio), "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                     capture_output=True).stdout
x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
n = len(x) // 8000
rms = np.sqrt((x[:n * 8000].reshape(n, 8000) ** 2).mean(1))
med = float(np.median(rms)) or 1e-6
m = WhisperModel(arg("--modelo", "base"), device="cpu", compute_type="int8")
segs, _ = m.transcribe(str(audio), vad_filter=True, beam_size=1)
filas = []
with (out / "transcripcion.tsv").open("w", encoding="utf-8") as f:
    for s in segs:
        a, b = int(s.start), max(int(s.end), int(s.start) + 1)
        vol = float(rms[a:b].max() / med) if a < n else 0
        filas.append((s.start, s.end, vol, s.text.strip()))
        f.write(f"{hms(s.start)}\t{hms(s.end)}\t{vol:.1f}\t{s.text.strip()}\n")
# puntuación por ventanas de 45 s: volumen máximo + nº de palabras de reacción
ventanas = {}
for a, b, vol, t in filas:
    k = int(a // 45)
    v = ventanas.setdefault(k, [0.0, 0, []])
    v[0] = max(v[0], vol)
    v[1] += len(REACCION.findall(t))
    v[2].append(t)
punt = sorted(ventanas.items(), key=lambda kv: -(kv[1][0] + 0.8 * kv[1][1]))
elegidas = []
for k, v in punt:
    if all(abs(k - e) >= 6 for e, _ in elegidas):  # separadas ≥4,5 min
        elegidas.append((k, v))
    if len(elegidas) >= int(arg("--top", 15)):
        break
with (out / "candidatos.txt").open("w", encoding="utf-8") as f:
    for k, v in sorted(elegidas):
        f.write(f"{hms(k * 45)}  vol x{v[0]:.1f}  reacciones {v[1]}  | {' / '.join(v[2])[:220]}\n")
audio.unlink()
print(f"ok {info.get('title', '')[:60]} · {len(filas)} frases · {out / 'candidatos.txt'}")
