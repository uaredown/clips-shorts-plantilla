"""Momentos virales de un VOD de Twitch por PICOS DE CHAT (método del reel 2026-11-19, shared/investigaciones/...-reel-picos-chat.md).
Baja el chat con TwitchDownloaderCLI (bin/, gratis, ~30 s por hora de VOD), cuenta mensajes cada 10 s (las reacciones pesan más)
y da los N mejores picos. El chat reacciona tarde → cada candidato empieza 20 s ANTES del pico.
Uso: python picos_chat.py <url o id del VOD> [--desde 0:00:00 --hasta 2:00:00] [--top 12] [--min-sep 90] [--todo]
Solo cuenta los capítulos del VOD en los que juega a GTA (--todo = sin filtrar).
Salida: output/_vods/v<id>/chat.json + picos.txt. Después: descargar_clip.py <slug> <url VOD> --desde .. --hasta .. (solo ese tramo, 1080p).
"""
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CLI = RAIZ / "bin" / "TwitchDownloaderCLI.exe"
RUIDO = re.compile(r"^\W*(\d{1,3}|\w)\W*$|giveaway|keyword|!enter|!join|gifted|\bsubs?\b", re.I)  # sorteos ("1", keyword) y letras sueltas
SEXUAL = re.compile(r"\bay+o+\b|freak|feeling nice|gya+t|bbl|🍑|🥵|strip|cake|thick|booty|\bass\b|tits|boob|naked|nude|horny|😩|🤤", re.I)
REACCION = re.compile(r"(lmf?ao|kekw|omegalul|lul|icant|😭|💀|🤣|😂|wtf|w+tf|no way|clip|holy|bro what|aware|wha+t)", re.I)


def arg(n, d=None):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d


def seg(t):  # "1:02:03" → s
    p = [float(x) for x in str(t).split(":")]
    return sum(v * 60 ** i for i, v in enumerate(reversed(p)))


def hms(s):
    s = int(s)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


vid = re.search(r"(\d{6,})", sys.argv[1]).group(1)
top, sep = int(arg("--top", 12)), int(arg("--min-sep", 90))
out = RAIZ.parents[1] / "output" / "_vods" / f"v{vid}"
out.mkdir(parents=True, exist_ok=True)
chat = out / "chat.json"
cmd = [str(CLI), "chatdownload", "--id", vid, "-o", str(chat), "--banner", "false", "--collision", "Overwrite"]
if arg("--desde"):
    cmd += ["-b", str(int(seg(arg("--desde"))))]
if arg("--hasta"):
    cmd += ["-e", str(int(seg(arg("--hasta"))))]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode or not chat.exists():
    sys.exit("TwitchDownloaderCLI falló: " + (r.stderr or r.stdout).strip()[-300:])

# solo tramos en los que juega a GTA (capítulos del VOD; en maratones 24/7 el chat también se dispara en "Just Chatting")
info = subprocess.run([str(CLI), "info", "--id", vid, "--format", "table", "--banner", "false"], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout or ""
gta = [(seg(a), seg(b)) for a, b in re.findall(r"Grand Theft Auto[^│]*│[^│]*│\s*([\d:]+)\s*│\s*([\d:]+)", info)]
if not gta and "--todo" not in sys.argv:
    sys.exit("el VOD no tiene capítulos de GTA (usar --todo para analizarlo igual)")

com = json.loads(chat.read_text(encoding="utf-8"))["comments"]
cubo, total, sexual = Counter(), Counter(), Counter()
for c in com:
    t = c["content_offset_seconds"]
    if gta and not any(a + 30 <= t <= b for a, b in gta):
        continue
    b = int(t // 10)
    total[b] += 1
    if SEXUAL.search(c["message"]["body"]):  # el chat delata las escenas sexuales (club de estriptis...): ese tramo no vale
        sexual[b] += 1
    if RUIDO.search(c["message"]["body"].strip()):
        continue
    if REACCION.search(c["message"]["body"]):  # solo cuentan las reacciones (risas, 💀, wtf...): los picos de mensajes normales eran sorteos/paneles
        cubo[b] += 1
for b in list(cubo):  # tramo de ±30 s con >4 % de mensajes sexuales → fuera
    vent = range(b - 3, b + 4)
    if sum(sexual[k] for k in vent) > 0.04 * max(1, sum(total[k] for k in vent)):
        del cubo[b]
if not cubo:
    sys.exit("sin mensajes en ese tramo")
media = sum(cubo.values()) / max(1, max(cubo) - min(cubo) + 1)
elegidos = []
for b, v in sorted(cubo.items(), key=lambda kv: -kv[1]):
    if all(abs(b * 10 - e) >= sep for e, _ in elegidos):
        elegidos.append((b * 10, v))
    if len(elegidos) >= top:
        break
lineas = [f"VOD {vid} · {len(com)} mensajes · media {media:.0f} pts/10 s · GTA: " + ", ".join(f"{hms(a)}-{hms(b)}" for a, b in gta)]
for t, v in sorted(elegidos):
    lineas.append(f"{hms(max(0, t - 20))} → {hms(t + 15)}  pico {hms(t)}  x{v / media:.1f}  "
                  f"descargar: --desde {hms(max(0, t - 20))} --hasta {hms(t + 15)}")
(out / "picos.txt").write_text("\n".join(lineas), encoding="utf-8")
print("\n".join(lineas))
