"""Lee shared/permisos-streamers.md y devuelve el estado de un streamer (lo usan descargar_clip.py y qa.py).
Uso: python permisos.py [streamer]   → sin argumento lista todos.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
TABLA = RAIZ / "shared" / "permisos-streamers.md"


def todos():
    filas = {}
    for linea in TABLA.read_text(encoding="utf-8").splitlines():
        c = [x.strip() for x in linea.strip().strip("|").split("|")]
        if len(c) >= 6 and c[0] not in ("streamer", "") and not c[0].startswith("---"):
            filas[c[0].lower()] = {"streamer": c[0], "plataforma": c[1], "idioma": c[2], "estado": c[3],
                                   "prueba": c[4], "comprobado": c[5]}
    return filas


def estado(streamer):
    return todos().get(streamer.lower(), {"estado": "desconocido"})


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(estado(sys.argv[1]))
    else:
        for f in todos().values():
            print(f"{f['estado']:10} {f['streamer']:15} {f['plataforma']:12} {f['idioma']}")
