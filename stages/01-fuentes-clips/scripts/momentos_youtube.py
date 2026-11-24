"""Momentos virales de un vídeo/VOD de YouTube según su "lo más repetido" (heatmap): los picos son lo que la gente vuelve a ver.
Uso: python momentos_youtube.py <url> [--top 8] [--min-sep 120]
Imprime: inicio–fin (hh:mm:ss) y la intensidad (0-1) de los N picos, separados al menos min-sep segundos.
Los directos recién terminados tardan en tener heatmap; para directos en vivo usar buscar_clips.py (clips de Twitch) o --directo.
"""
import json
import subprocess
import sys


def arg(n, d):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d


def hms(s):
    s = int(s)
    return f"{s // 3600}:{s // 60 % 60:02d}:{s % 60:02d}"


url, top, sep = sys.argv[1], int(arg("--top", 8)), float(arg("--min-sep", 120))
r = subprocess.run(["yt-dlp", "--js-runtimes", "node", "-J", "--no-playlist", url], capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
if r.returncode:
    sys.exit("yt-dlp falló: " + (r.stderr.strip().splitlines() or ["?"])[-1][:200])
j = json.loads(r.stdout)
hm = j.get("heatmap") or []
print(f"{j.get('channel')} · {j.get('title', '')[:70]} · {int(j.get('duration') or 0) // 60} min · {j.get('view_count')} vistas")
if not hm:
    sys.exit("sin heatmap (vídeo nuevo o con pocas vistas)")
elegidos = []
for h in sorted(hm, key=lambda h: -h["value"]):
    if all(abs(h["start_time"] - e["start_time"]) >= sep for e in elegidos):
        elegidos.append(h)
    if len(elegidos) >= top:
        break
for h in sorted(elegidos, key=lambda h: h["start_time"]):
    print(f"  {hms(h['start_time'])}–{hms(h['end_time'])}  intensidad {h['value']:.2f}")
