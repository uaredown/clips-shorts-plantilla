"""Recorta fuente.mp4 (etapa 01) según seleccion.json → stages/02-seleccion-gancho/output/<slug>/clip.mp4.
Uso: python recortar.py <short-NNN-slug>
Comprueba antes: campos obligatorios de seleccion.json, aporte propio no vacío, sin spoiler, sin música con copyright,
y que la duración final (con segmentos/replay) sea ≤59 s.
"""
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
OBLIG = ["streamer", "canal_url", "desde", "hasta", "momento", "aporte", "gancho", "tipo_gancho", "estructura",
         "layout", "acento", "fuente", "pos_subs", "pregunta", "bucle", "spoiler", "musica_con_copyright"]

slug = sys.argv[1]
d02 = RAIZ / "stages/02-seleccion-gancho/output" / slug
s = json.loads((d02 / "seleccion.json").read_text(encoding="utf-8"))
falta = [k for k in OBLIG if k not in s or s[k] in ("", None)]
if falta:
    sys.exit(f"seleccion.json incompleto: {falta}")
if s["spoiler"] or s["musica_con_copyright"]:
    sys.exit("BLOQUEADO: spoiler de historia o música con copyright")
if len(s["aporte"].split()) < 6:
    sys.exit("BLOQUEADO: 'aporte' demasiado pobre (contexto propio, ≥6 palabras)")
dur = s["hasta"] - s["desde"]
segs = s.get("segmentos") or [{"desde": 0, "hasta": dur, "vel": 1}]
total = sum((g["hasta"] - g["desde"]) / g.get("vel", 1) for g in segs)
if total > 59:
    sys.exit(f"BLOQUEADO: duración final {total:.1f}s > 59 s")
src = RAIZ / "stages/01-fuentes-clips/output" / slug / "fuente.mp4"
r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s["desde"]), "-i", str(src), "-t", f"{dur:.3f}",
                    "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-r", "30", "-c:a", "aac", "-b:a", "192k",
                    str(d02 / "clip.mp4")], capture_output=True, text=True)
if r.returncode:
    sys.exit(r.stderr[-300:])
print(f"ok clip.mp4 · {dur:.1f}s de fuente · final previsto {total:.1f}s · {s['layout']}/{s['tipo_gancho']}/{s['estructura']}")
