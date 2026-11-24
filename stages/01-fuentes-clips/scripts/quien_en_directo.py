"""¿Quién está en directo ahora? Lee shared/streamers.json y mira Twitch/YouTube con yt-dlp (sin descargar nada).
Uso: python quien_en_directo.py   → una línea por streamer en directo (plataforma, título, url), por prioridad.
Es el primer paso de cada vuelta del horario de 30 min (shared/horario-clipping.md).
"""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
S = json.loads((RAIZ / "shared/streamers.json").read_text(encoding="utf-8"))


def mirar(nombre, plat, canal):
    url = f"https://www.twitch.tv/{canal}" if plat == "twitch" else f"https://www.youtube.com/{canal}/live"
    cmd = ["yt-dlp", "-J", "--no-playlist", url] + (["--js-runtimes", "node"] if plat == "youtube" else [])
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90)
    try:
        j = json.loads(r.stdout)
    except Exception:  # noqa: BLE001  (no está en directo → yt-dlp da error)
        return None
    if j and (j.get("is_live") or j.get("live_status") == "is_live"):
        return (S[nombre]["prioridad"], nombre, plat, (j.get("description") or j.get("title") or "")[:70], url)
    return None


tareas = [(n, p, c[p]) for n, c in S.items() if not n.startswith("_") for p in ("twitch", "youtube") if p in c]
with ThreadPoolExecutor(6) as ex:
    vivos = [r for r in ex.map(lambda t: mirar(*t), tareas) if r]
for pr, n, p, t, u in sorted(vivos):
    print(f"[{pr}] {n:14} {p:7} {t} · {u}")
print(f"{len(vivos)} en directo de {len(tareas)} canales")
sys.exit(0)
