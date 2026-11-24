"""Recopilación: une 3-4 momentos (de grabaciones/clips ya descargados) en un fuente.mp4 vertical 1080×1920.
Cada parte = zona del juego (sin facecam/chat/subtítulos quemados) en grande sobre su propio fondo desenfocado.
Uso: python recopilar.py <short-NNN-slug>     (lee output/<slug>/recopilacion.json)
{"tema": "GTA 6 NPCs", "partes": [{"fuente": "short-022-raw-tomo1", "desde": 12.0, "hasta": 18.5, "juego": [x, y, w, h]}, ...]}
Después: seleccion.json en 02 con "layout": "zoom" (la fuente ya es vertical), "creditos": [{"streamer", "canal_url"}, ...].
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "output"
slug = sys.argv[1]
d = OUT / slug
cfg = json.loads((d / "recopilacion.json").read_text(encoding="utf-8"))
partes = cfg["partes"]

ent, fil = [], []
for i, p in enumerate(partes):
    ent += ["-ss", str(p["desde"]), "-t", str(round(p["hasta"] - p["desde"], 3)), "-i", str(OUT / p["fuente"] / "fuente.mp4")]
    x, y, w, h = p.get("juego", [0, 0, 1, 1])
    fil.append(f"[{i}:v]crop=iw*{w}:ih*{h}:iw*{x}:ih*{y},fps=30,split[a{i}][b{i}];"
               f"[a{i}]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:3,eq=brightness=-0.15[bg{i}];"
               f"[b{i}]scale=1080:-2[fg{i}];[bg{i}][fg{i}]overlay=0:(H-h)/2,setsar=1,format=yuv420p[v{i}];"
               f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-1.5[s{i}]")
fil.append("".join(f"[v{i}][s{i}]" for i in range(len(partes))) + f"concat=n={len(partes)}:v=1:a=1[v][a]")
r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-sws_flags", "lanczos+accurate_rnd+full_chroma_int", *ent, "-filter_complex", ";".join(fil), "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-crf", "14", "-preset", "slow", "-c:a", "aac", "-b:a", "192k", str(d / "fuente.mp4")],
                   capture_output=True, text=True)
if r.returncode:
    sys.exit("ffmpeg falló: " + r.stderr.strip()[-300:])

fuentes = [json.loads((OUT / p["fuente"] / "fuente.json").read_text(encoding="utf-8")) for p in partes]
dur = round(sum(p["hasta"] - p["desde"] for p in partes), 2)
(d / "fuente.json").write_text(json.dumps({
    "slug": slug, "recopilacion": True, "tema": cfg.get("tema", ""), "idioma_tabla": "en", "prueba": False,
    "permiso": "ok" if all(f["permiso"] == "ok" for f in fuentes) else "revisar",
    "partes": [{"fuente": p["fuente"], "url": f["url"], "streamer": f["streamer"], "desde": p["desde"], "hasta": p["hasta"]}
               for p, f in zip(partes, fuentes)],
    "duracion": dur, "descargado": datetime.now(timezone.utc).isoformat(timespec="seconds")}, ensure_ascii=False, indent=1),
    encoding="utf-8")
print(f"ok {slug}/fuente.mp4 · {len(partes)} partes · {dur}s · streamers: {', '.join(f['streamer'] for f in fuentes)}")
