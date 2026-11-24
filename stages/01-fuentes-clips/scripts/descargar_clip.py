"""Descarga un clip (o un tramo de un VOD) a stages/01-fuentes-clips/output/<slug>/fuente.mp4 + fuente.json.
Uso: python descargar_clip.py <short-NNN-slug> <url> --streamer <nombre> [--desde 1:23:05 --hasta 1:23:50] [--prueba]
     python descargar_clip.py <slug> https://www.twitch.tv/<canal> --streamer <s> --directo 150   (graba 150 s del directo en vivo)
- Se niega si el streamer no tiene estado ok en shared/permisos-streamers.md (salvo --prueba: solo para pruebas, nunca se publica).
- Tramo de VOD: máx. 90 s (luego 02 recorta a ≤59 s).
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import permisos  # noqa: E402

RAIZ = Path(__file__).resolve().parents[3]


def arg(nombre, defecto=None):
    return sys.argv[sys.argv.index(nombre) + 1] if nombre in sys.argv else defecto


def seg(t):
    s = 0.0
    for p in str(t).split(":"):
        s = s * 60 + float(p)
    return s


slug, url, streamer = sys.argv[1], sys.argv[2], arg("--streamer")
prueba = "--prueba" in sys.argv
if not streamer:
    sys.exit("Falta --streamer")
perm = permisos.estado(streamer)
if perm["estado"] not in ("ok", "riesgo") and not prueba:
    sys.exit(f"BLOQUEADO: {streamer} tiene estado '{perm['estado']}' en shared/permisos-streamers.md")
desde, hasta = arg("--desde"), arg("--hasta")
if desde and hasta and seg(hasta) - seg(desde) > 90:
    sys.exit("Tramo >90 s: acota más (el Short final es ≤59 s)")

out = RAIZ / "stages/01-fuentes-clips/output" / slug
out.mkdir(parents=True, exist_ok=True)
info = subprocess.run(["yt-dlp", "-J", "--no-playlist", url], capture_output=True, text=True,
                      encoding="utf-8", errors="replace")
if info.returncode:
    sys.exit("yt-dlp -J falló: " + (info.stderr.strip().splitlines() or ["?"])[-1][:200])
j = json.loads(info.stdout)
cmd = ["yt-dlp", "-q", "--no-progress", "--no-playlist", "-f", "bv*[height<=1080][format_id!*=portrait]+ba/b[height<=1080][format_id!*=portrait]/b",
       "--merge-output-format", "mp4", "-o", str(out / "fuente.%(ext)s"), "--force-overwrites"]
if desde and hasta:
    cmd += ["--download-sections", f"*{desde}-{hasta}", "--force-keyframes-at-cuts"]
if arg("--directo"):  # graba N segundos del directo en vivo desde ahora (luego 02 elige el momento)
    cmd += ["--downloader", "ffmpeg", "--downloader-args", f"ffmpeg:-t {int(arg('--directo'))}"]
if "youtube.com" in url or "youtu.be" in url:
    cmd += ["--js-runtimes", "node"]  # sin motor JS faltan formatos de YouTube (2026-11-18)
r = subprocess.run(cmd + [url], capture_output=True, text=True, encoding="utf-8", errors="replace")
mp4 = out / "fuente.mp4"
if r.returncode or not mp4.exists():
    sys.exit("descarga falló: " + (r.stderr.strip().splitlines() or ["?"])[-1][:200])
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
                           capture_output=True, text=True).stdout.strip() or 0)
meta = {"slug": slug, "url": url, "streamer": streamer, "plataforma": perm.get("plataforma", ""),
        "idioma_tabla": perm.get("idioma", ""), "permiso": perm["estado"], "prueba": prueba,
        "titulo_original": j.get("title"), "canal": j.get("uploader") or j.get("channel"),
        "fecha_original": j.get("upload_date") or j.get("timestamp"), "vistas_original": j.get("view_count"),
        "desde": desde, "hasta": hasta, "duracion": round(dur, 2),
        "descargado": datetime.now(timezone.utc).isoformat(timespec="seconds")}
(out / "fuente.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
print(("AVISO: streamer SIN permiso (riesgo aceptado por el usuario) · " if perm["estado"] == "riesgo" else "") + f"ok {mp4.relative_to(RAIZ)} · {dur:.1f}s · {meta['titulo_original']} · permiso {perm['estado']}")
