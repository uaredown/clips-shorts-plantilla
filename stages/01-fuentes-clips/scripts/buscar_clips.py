"""Lista los clips más vistos de un streamer (Twitch o Kick) sin descargar nada. Salida corta (top N).
Uso: python buscar_clips.py <streamer> [--plataforma twitch|kick] [--rango 24hr|7d|30d|all] [--top 15]
Solo para streamers con estado ok/pendiente en shared/permisos-streamers.md.
Twitch: https://www.twitch.tv/<s>/clips?filter=clips&range=<rango>  ·  Kick: https://kick.com/<s>/clips
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import permisos  # noqa: E402


def arg(nombre, defecto):
    return sys.argv[sys.argv.index(nombre) + 1] if nombre in sys.argv else defecto


streamer = sys.argv[1]
plat, rango, top = arg("--plataforma", "twitch"), arg("--rango", "24hr"), int(arg("--top", "15"))
est = permisos.estado(streamer)["estado"]
if est not in ("ok", "riesgo", "pendiente"):
    sys.exit(f"{streamer}: estado '{est}' en permisos-streamers.md → no se clipea")
url = (f"https://www.twitch.tv/{streamer}/clips?filter=clips&range={rango}" if plat == "twitch"
       else f"https://kick.com/{streamer}/clips")
r = subprocess.run(["yt-dlp", "--flat-playlist", "-J", "--playlist-end", str(top * 3), url],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
if r.returncode:
    sys.exit("yt-dlp falló: " + r.stderr.strip().splitlines()[-1][:200] if r.stderr.strip() else "yt-dlp falló")
ent = json.loads(r.stdout).get("entries") or []
ent.sort(key=lambda e: -(e.get("view_count") or 0))
for e in ent[:top]:
    print(f"{e.get('view_count') or 0:>8} vistas · {e.get('duration') or 0:>4.0f}s · {(e.get('title') or '')[:60]} · {e.get('url')}")
print(f"{len(ent)} clips encontrados ({streamer}, {plat}, {rango}); permiso: {est}")
