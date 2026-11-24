"""Variedad entre Shorts seguidos (política de contenido "no auténtico" de YouTube; idea de variedad_check.py de Cathode Files).
Lee stages/02-seleccion-gancho/output/short-*/seleccion.json en orden de número.
Uso:
  python variedad_check.py check <short-NNN-slug>   → sale 1 si choca con los anteriores (montar.py lo llama solo)
  python variedad_check.py tabla [N]                → firma de los últimos N (def. 10)
"""
import difflib
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
SEL = RAIZ / "stages/02-seleccion-gancho/output"

# ---- REGLAS (cambiar solo aquí) ----
REGLAS = {
    "tipo_gancho_ventana": 2,    # el mismo tipo de gancho no puede salir en los N anteriores
    "estructura_ventana": 1,     # la misma estructura no en el anterior
    "acento_ventana": 2,         # el mismo color de acento no en los N anteriores
    "fuente_ventana": 1,         # la misma tipografía no en el anterior
    "layout_racha_max": 2,       # el mismo layout como mucho N seguidos (incluido este)
    "plantilla_ventana": 4,      # misma combinación layout+acento+fuente+pos_subs no en los N anteriores
    "streamer_racha_max": 3,     # el mismo streamer como mucho N seguidos (3 desde 2026-11-18: calentamiento con solo Speed y Kai)
    "texto_parecido_max": 0.6,   # gancho/pregunta no más parecidos que esto (0-1) a los…
    "texto_ventana": 15,         # …N anteriores
}


def num(slug):
    m = re.match(r"short-(\d+)", slug)
    return int(m.group(1)) if m else -1


def todos():
    out = []
    for f in SEL.glob("short-*/seleccion.json"):
        s = json.loads(f.read_text(encoding="utf-8"))
        s["slug"] = f.parent.name
        out.append(s)
    return sorted(out, key=lambda s: num(s["slug"]))


def parecido(a, b):
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def check(slug):
    lista = todos()
    yo = next((s for s in lista if s["slug"] == slug), None)
    if not yo:
        return [f"no existe seleccion.json de {slug}"]
    prev = [s for s in lista if num(s["slug"]) < num(slug) and not s.get("prueba")][::-1]  # más reciente primero
    R, err = REGLAS, []

    def ventana(campo, n):
        if any(p.get(campo) == yo.get(campo) for p in prev[:n]):
            err.append(f"{campo} '{yo.get(campo)}' repetido en los {n} anteriores")
    ventana("tipo_gancho", R["tipo_gancho_ventana"])
    ventana("estructura", R["estructura_ventana"])
    ventana("acento", R["acento_ventana"])
    ventana("fuente", R["fuente_ventana"])
    firma = lambda s: (s.get("layout"), s.get("acento"), s.get("fuente"), s.get("pos_subs"),  # noqa: E731
                       s.get("subs_estilo", "grupo"), bool(s.get("titular")))
    if any(firma(p) == firma(yo) for p in prev[:R["plantilla_ventana"]]):
        err.append(f"plantilla visual {firma(yo)} repetida en los {R['plantilla_ventana']} anteriores")
    for campo, maxi in (("layout", R["layout_racha_max"]), ("streamer", R["streamer_racha_max"])):
        racha = 1
        for p in prev:
            if p.get(campo) != yo.get(campo):
                break
            racha += 1
        if racha > maxi:
            err.append(f"{campo} '{yo.get(campo)}' {racha} seguidos (máx {maxi})")
    for campo in ("gancho", "pregunta"):
        for p in prev[:R["texto_ventana"]]:
            r = parecido(yo.get(campo, ""), p.get(campo, ""))
            if r > R["texto_parecido_max"]:
                err.append(f"{campo} demasiado parecido a {p['slug']} ({r:.2f}): '{p.get(campo)}'")
    return err


if __name__ == "__main__":
    if sys.argv[1] == "check":
        e = check(sys.argv[2])
        print("VARIEDAD OK" if not e else "VARIEDAD FALLA:\n- " + "\n- ".join(e))
        sys.exit(1 if e else 0)
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    for s in todos()[-n:]:
        print(f"{s['slug'][:28]:28} {s.get('streamer', '')[:12]:12} {s.get('layout'):6} {s.get('tipo_gancho', '')[:12]:12} "
              f"{s.get('estructura', '')[:16]:16} {s.get('acento')} {s.get('fuente', '')[:10]:10} {s.get('pos_subs')}")
