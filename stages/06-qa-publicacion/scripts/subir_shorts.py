"""Cola de subida de Shorts (base: subir_shorts.py de Bow Tie Mind, 2026-11-17). Sube como PRIVADO PROGRAMADO (publishAt),
verifica con la API, apunta el enlace en el registro semanal y borra los temporales grandes (fuente.mp4, clip.mp4).
Uso:
  python subir_shorts.py plan              # cola (meta.json con QA ok y sin subido.json) y hueco que le toca a cada uno
  python subir_shorts.py subir [N]         # sube los N siguientes (def. 1; cuota ≈ 2.050 c/u con subtítulos y playlist)
  python subir_shorts.py subir 1 --ya      # el siguiente sale en ~20 min (para momentos en caliente del lanzamiento)
  python subir_shorts.py subir 1 --huecos 02:15,03:15   # usar otras horas (UTC) en vez de HUECOS_UTC
Huecos: HUECOS_UTC cada día, nunca dos a menos de SEPARACION_MIN. Estado: subido.json en cada carpeta de 06.
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import youtube_api as Y  # noqa: E402

RAIZ = Path(__file__).resolve().parents[3]
PUB = RAIZ / "stages/06-qa-publicacion/output"
REG = RAIZ / "shared/registros"
HUECOS_UTC = ["13:00", "16:00", "18:00", "20:00", "22:30"]  # 5/día; 17-20 UTC es la franja fuerte (investigación 2026-11-17)
SEPARACION_MIN = 90


def ocupados():  # horas ya usadas: subidos por API + paquetes manuales
    fs = list(PUB.glob("short-*/subido.json")) + list(PUB.glob("short-*/manual.json"))
    return sorted({datetime.fromisoformat(json.loads(f.read_text(encoding="utf-8"))["publicar_en"].replace("Z", "+00:00"))
                   for f in fs})


def cola():
    out = []
    for m in sorted(PUB.glob("short-*/meta.json")):
        d = m.parent
        qa = json.loads((d / "qa.json").read_text(encoding="utf-8")) if (d / "qa.json").exists() else {}
        if qa.get("ok") and not (d / "subido.json").exists() and not (d / "manual.json").exists():
            out.append(d.name)
    return out


def libre(ocup, ya=False):
    ahora = datetime.now(timezone.utc)
    if ya:
        t = (ahora + timedelta(minutes=20)).replace(second=0, microsecond=0)
        if all(abs((t - o).total_seconds()) >= 30 * 60 for o in ocup):
            return t
    dia = ahora.date()
    while True:
        for h in HUECOS_UTC:
            t = datetime.fromisoformat(f"{dia}T{h}:00+00:00")
            if t > ahora + timedelta(minutes=30) and all(abs((t - o).total_seconds()) >= SEPARACION_MIN * 60 for o in ocup):
                return t
        dia += timedelta(days=1)


def registrar(slug, meta, vid, cuando):
    REG.mkdir(parents=True, exist_ok=True)
    a, s, _ = cuando.isocalendar()
    f = REG / f"registro-{a}-W{s:02d}.md"
    if not f.exists():
        f.write_text(f"# Registro semana {a}-W{s:02d}\n\n| slug | idioma | título | enlace | sale (UTC) | vistas 48h | % visto | "
                     "visto vs desliz. | notas |\n|---|---|---|---|---|---|---|---|---|\n", encoding="utf-8")
    with f.open("a", encoding="utf-8") as fh:
        fh.write(f"| {slug} | {meta['idioma']} | {meta['titulo'][:60]} | https://youtu.be/{vid} | "
                 f"{cuando:%m-%d %H:%M} | | | | |\n")
    return f


def main():
    global HUECOS_UTC, SEPARACION_MIN
    if "--sep" in sys.argv:  # separación mínima en minutos (def. 90)
        SEPARACION_MIN = int(sys.argv[sys.argv.index("--sep") + 1])
    if "--huecos" in sys.argv:  # p. ej. --huecos 02:15,03:15,04:15 (calentamiento / noches especiales)
        HUECOS_UTC = sys.argv[sys.argv.index("--huecos") + 1].split(",")
    accion = sys.argv[1] if len(sys.argv) > 1 else "plan"
    ocup, c = ocupados(), cola()
    if accion == "plan":
        tmp = list(ocup)
        for slug in c:
            t = libre(tmp)
            tmp.append(t)
            print(f"{t:%Y-%m-%d %H:%M} UTC · {slug}")
        print(f"{len(ocup)} ya programados · {len(c)} en cola")
        return
    n = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 1
    for slug in c[:n]:
        d = PUB / slug
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        t = libre(ocup, ya="--ya" in sys.argv)
        meta["publicar_en"] = t.strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"== {slug} @ {meta['publicar_en']}", flush=True)
        vid = Y.subir(meta)
        (d / "subido.json").write_text(json.dumps({"id": vid, "url": f"https://youtu.be/{vid}",
                                                   "publicar_en": meta["publicar_en"]}, indent=1), encoding="utf-8")
        ok = Y.verificar(vid, meta["publicar_en"])
        f = registrar(slug, meta, vid, t)
        ocup.append(t)
        for tmp in (RAIZ / "stages/01-fuentes-clips/output" / slug / "fuente.mp4",
                    RAIZ / "stages/02-seleccion-gancho/output" / slug / "clip.mp4"):
            tmp.unlink(missing_ok=True)
        print(f"  {'verificado' if ok else 'REVISAR EN STUDIO'} · registro {f.name} · temporales borrados")


if __name__ == "__main__":
    main()
