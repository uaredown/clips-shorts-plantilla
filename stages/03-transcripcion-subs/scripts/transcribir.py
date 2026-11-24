"""Transcribe clip.mp4 (etapa 02) con faster-whisper (gratis, local) con tiempos por palabra.
Uso: python transcribir.py <short-NNN-slug> [--modelo small|medium] [--idioma en] [--fuente] [--sin-vad]  (--sin-vad: audio con mucho ruido de juego donde el VAD se come la voz)
Salida en stages/03-transcripcion-subs/output/<slug>/: palabras.json ({"idioma", "palabras":[{"w","s","e"}]}) y texto.txt
(texto corrido para revisarlo/corregirlo: si corriges, edita palabras.json, no texto.txt).
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
from faster_whisper import WhisperModel  # noqa: E402

RAIZ = Path(__file__).resolve().parents[3]


def arg(n, d=None):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d


slug = sys.argv[1]
clip = RAIZ / "stages/02-seleccion-gancho/output" / slug / "clip.mp4"
if "--fuente" in sys.argv:  # transcribir fuente.mp4 de 01 directamente (válido si seleccion.json usa desde=0)
    clip = RAIZ / "stages/01-fuentes-clips/output" / slug / "fuente.mp4"
out = RAIZ / "stages/03-transcripcion-subs/output" / slug
out.mkdir(parents=True, exist_ok=True)
modelo = WhisperModel(arg("--modelo", "small"), device="cpu", compute_type="int8")
segs, info = modelo.transcribe(str(clip), language=arg("--idioma"), word_timestamps=True, vad_filter="--sin-vad" not in sys.argv,
                               beam_size=5)
palabras = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)}
            for sg in segs for w in (sg.words or []) if w.word.strip()]
# tacos con asterisco en el subtítulo (el audio no se toca); insultos raciales siempre tapados
import re  # noqa: E402
CENSURA = [(r"(?i)\bf(u)(ck\w*)", r"f*\2"), (r"(?i)\bs(h)(it\w*)", r"s*\2"), (r"(?i)\bb(i)(tch\w*)", r"b*\2"),
           (r"(?i)\bn(i)(gg\w*)", r"n****"), (r"(?i)\bp(u)(ssy\w*)", r"p*\2"), (r"(?i)\bd(i)(ck\w*)", r"d*\2")]
for p in palabras:
    for pat, rep in CENSURA:
        p["w"] = re.sub(pat, rep, p["w"])
# whisper separa a veces "y 'all" / "62 ,000": juntar con la palabra anterior
fus = []
for p in palabras:
    if fus and p["w"][:1] in ("'", ","):
        fus[-1]["w"] += p["w"]
        fus[-1]["e"] = p["e"]
    else:
        fus.append(p)
palabras = fus
(out / "palabras.json").write_text(json.dumps({"idioma": info.language, "prob": round(info.language_probability, 2),
                                               "palabras": palabras}, ensure_ascii=False, indent=0), encoding="utf-8")
(out / "texto.txt").write_text(" ".join(p["w"] for p in palabras), encoding="utf-8")
print(f"ok {len(palabras)} palabras · idioma {info.language} ({info.language_probability:.0%}) · {out.relative_to(RAIZ)}")
