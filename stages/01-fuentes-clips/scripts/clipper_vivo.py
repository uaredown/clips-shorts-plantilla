"""Clipper EN VIVO (idea del reel de aiverse.pranav, 2026-11-20): graba el directo desde ya y corta solo cuando el chat explota.
Streamlink (salta anuncios) → trozos de 10 s en un búfer de 10 min · chat de Twitch anónimo (sin login) · picos cada 10 s
(las reacciones pesan más, sorteos y tramos sexuales no cuentan) → ffmpeg une 25 s antes + 10 s después del pico.
Uso: python clipper_vivo.py <canal_twitch> [--minutos 60] [--umbral 3] [--min 8] [--pausa 60]
Salida: output/_vivo/<canal>/<hora>_p<puntos>.mp4 + picos.txt (mensajes del pico). Luego revisar a ojo (¿es GTA? ¿sin strip club?)
y seguir con descargar_clip.py/02 como un clip más. Solo streamers `ok`.
"""
import re
import socket
import subprocess
import sys
import threading
import time
from collections import deque
from pathlib import Path
from statistics import median

RAIZ = Path(__file__).resolve().parents[1]
RUIDO = re.compile(r"^\W*(\d{1,3}|\w)\W*$|giveaway|keyword|!enter|!join|gifted|\bsubs?\b", re.I)
SEXUAL = re.compile(r"\bay+o+\b|freak|feeling nice|gya+t|bbl|🍑|🥵|strip|cake|thick|booty|\bass\b|tits|boob|naked|nude|horny|😩|🤤", re.I)
REACCION = re.compile(r"(lmf?ao|kekw|omegalul|lul|icant|😭|💀|🤣|😂|wtf|w+tf|no way|clip|holy|bro what|aware|wha+t)", re.I)
VENTANA, ANTES, DESPUES, BUFER = 10, 25, 10, 600


def arg(n, d=None):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d


canal = sys.argv[1].lower().rstrip("/").split("/")[-1]
fin = time.time() + float(arg("--minutos", 60)) * 60
umbral, minimo, pausa = float(arg("--umbral", 3)), float(arg("--min", 8)), float(arg("--pausa", 60))
out = RAIZ / "output" / "_vivo" / canal
segs = out / "segs"
segs.mkdir(parents=True, exist_ok=True)
for f in segs.glob("*.ts"):
    f.unlink()

# 1) grabación: streamlink → ffmpeg en trozos de 10 s
sl = subprocess.Popen([sys.executable, "-m", "streamlink", "-O", "--hls-live-edge", "2", f"https://www.twitch.tv/{canal}", "best"],
                      stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-i", "-", "-c", "copy", "-f", "segment", "-segment_time", str(VENTANA),
                       "-reset_timestamps", "1", str(segs / "s%06d.ts")], stdin=sl.stdout, stderr=subprocess.DEVNULL)
inicio_seg = {}  # nombre → hora real en que empezó a escribirse


def vigilar_trozos():
    while time.time() < fin and ff.poll() is None:
        for f in sorted(segs.glob("*.ts")):
            inicio_seg.setdefault(f.name, time.time())
            if time.time() - inicio_seg[f.name] > BUFER:
                f.unlink(missing_ok=True)
        time.sleep(1)


threading.Thread(target=vigilar_trozos, daemon=True).start()

# 2) chat anónimo (IRC de Twitch, usuario justinfan = solo lectura)
irc = socket.create_connection(("irc.chat.twitch.tv", 6667))
irc.settimeout(1)
irc.sendall(f"NICK justinfan{int(time.time()) % 100000}\r\nJOIN #{canal}\r\n".encode())
cubo, puntos, sexual, mensajes, historia = time.time(), 0.0, 0, [], deque(maxlen=30)  # historia = 5 min de ventanas
ultimo, buf, n = 0.0, "", 0
print(f"Vigilando #{canal} hasta {time.strftime('%H:%M', time.localtime(fin))} (umbral x{umbral}, mínimo {minimo})", flush=True)


def cortar(t_pico, pts, msgs):
    time.sleep(DESPUES + 3)
    a, b = t_pico - VENTANA - ANTES, t_pico + DESPUES
    trozos = [segs / k for k, t in sorted(inicio_seg.items(), key=lambda x: x[1]) if a <= t <= b and (segs / k).exists()]
    if not trozos:
        return
    nombre = time.strftime("%H%M%S", time.localtime(t_pico)) + f"_p{int(pts)}"
    lista = out / f"{nombre}.txt"
    lista.write_text("".join(f"file '{p.as_posix()}'\n" for p in trozos), encoding="utf-8")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy",
                    str(out / f"{nombre}.mp4")])
    lista.unlink()
    with open(out / "picos.txt", "a", encoding="utf-8") as f:
        f.write(f"{nombre}.mp4 · {pts:.0f} pts · " + " | ".join(msgs[:8]) + "\n")
    print(f"CLIP {nombre}.mp4 ({len(trozos) * VENTANA} s) · {' | '.join(msgs[:4])}", flush=True)


while time.time() < fin and ff.poll() is None:
    try:
        buf += irc.recv(4096).decode("utf-8", "replace")
    except socket.timeout:
        pass
    *lineas, buf = buf.split("\r\n")
    for ln in lineas:
        if ln.startswith("PING"):
            irc.sendall(b"PONG :tmi.twitch.tv\r\n")
        elif "PRIVMSG" in ln:
            txt = ln.split(" :", 1)[-1]
            if RUIDO.search(txt):
                continue
            sexual += bool(SEXUAL.search(txt))
            puntos += 3 if REACCION.search(txt) else 1
            mensajes.append(txt[:40])
    if time.time() - cubo >= VENTANA:
        base = median(historia) if len(historia) >= 6 else None
        es_pico = base is not None and puntos >= max(minimo, umbral * max(base, 1)) and sexual < len(mensajes) * 0.2
        if es_pico and time.time() - ultimo > pausa:
            ultimo, n = time.time(), n + 1
            threading.Thread(target=cortar, args=(time.time(), puntos, mensajes)).start()
        historia.append(puntos)
        cubo, puntos, sexual, mensajes = time.time(), 0.0, 0, []

time.sleep(DESPUES + 5)
for p in (ff, sl):
    p.terminate()
print(f"Fin: {n} clips en {out}")
