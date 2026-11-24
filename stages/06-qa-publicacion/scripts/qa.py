"""QA de un Short antes de publicarlo. Escribe stages/06-qa-publicacion/output/<slug>/qa.json y hoja.jpg (hoja de contacto
pequeña de 8 fotogramas: revisarla UNA vez, no fotograma a fotograma).
Uso: python qa.py <short-NNN-slug>      (sale 1 si algo falla)
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "stages/01-fuentes-clips/scripts"))
sys.path.insert(0, str(RAIZ / "stages/04-montaje/scripts"))
import permisos  # noqa: E402
import variedad_check  # noqa: E402

slug = sys.argv[1]
st = lambda n: RAIZ / "stages" / n / "output" / slug  # noqa: E731
out = st("06-qa-publicacion")
out.mkdir(parents=True, exist_ok=True)
err, aviso = [], []
sel = json.loads((st("02-seleccion-gancho") / "seleccion.json").read_text(encoding="utf-8"))
final = st("04-montaje") / "final.mp4"

if not final.exists():
    err.append("no existe final.mp4")
else:
    p = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height",
                                   "-show_entries", "format=duration", "-of", "json", str(final)],
                                  capture_output=True, text=True).stdout)
    v = next(s for s in p["streams"] if s["codec_type"] == "video")
    dur = float(p["format"]["duration"])
    if (v["width"], v["height"]) != (1080, 1920):
        err.append(f"resolución {v['width']}x{v['height']}")
    if dur > 59.5:
        err.append(f"dura {dur:.1f}s (>59)")
    if not any(s["codec_type"] == "audio" for s in p["streams"]):
        err.append("sin audio")
    if not (st("04-montaje") / "final.srt").exists():
        err.append("falta final.srt")
    n = 8
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(final), "-vf",
                    f"fps={n}/{dur:.2f},scale=180:320,tile={n // 2}x2", "-frames:v", "1", "-q:v", "5",
                    str(out / "hoja.jpg")], check=False)

if sel.get("prueba"):
    err.append("es una PRUEBA: nunca se publica")
if sel.get("spoiler") or sel.get("musica_con_copyright"):
    err.append("spoiler o música con copyright")
# Recopilación: "creditos": [{"streamer", "canal_url"}, ...] → permiso y crédito de cada uno
creditos = sel.get("creditos") or [{"streamer": sel.get("streamer", ""), "canal_url": sel.get("canal_url", "")}]
for c in creditos:
    perm = permisos.estado(c["streamer"])["estado"]
    if perm == "riesgo":
        aviso.append(f"{c['streamer']} SIN permiso: riesgo de strike aceptado por el usuario (retirar el mismo día si lo piden)")
    elif perm != "ok":
        err.append(f"permiso de {c['streamer']}: {perm}")
if not sel.get("prueba"):
    err += [f"variedad: {e}" for e in variedad_check.check(slug)]
seo_f = st("05-seo") / "seo.json"
if not seo_f.exists():
    err.append("falta 05-seo/seo.json")
else:
    seo = json.loads(seo_f.read_text(encoding="utf-8"))
    if len(seo["titulo"]) > 100:
        err.append("título >100")
    elif len(seo["titulo"]) > 70:
        aviso.append("título >70 caracteres (se corta en móvil)")
    cabecera = "\n".join(seo["descripcion"].splitlines()[:len(creditos)]).lower()
    for c in creditos:
        host = c["canal_url"].split("//")[-1].removeprefix("www.").rstrip("/")
        if host.lower() not in cabecera:
            err.append(f"las primeras líneas de la descripción no acreditan a {c['streamer']} ({host})")

    # Campañas de clipping (shared/campanas.json): seleccion.json "campanas": [...] + "miembros": [...] (quién sale)
    REGLAS_C = json.loads((RAIZ / "shared/campanas.json").read_text(encoding="utf-8"))
    norm = lambda x: x.lower().replace(" ", "")  # noqa: E731
    miembros = [norm(m) for m in sel.get("miembros", [])]
    mont = st("04-montaje") / "montaje.json"
    idioma = seo.get("idioma") or (json.loads(mont.read_text(encoding="utf-8"))["idioma"] if mont.exists() else "")
    tags_desc = norm(seo["descripcion"] + " " + " ".join(seo.get("hashtags", [])))
    texto = norm(seo["titulo"] + " " + sel.get("gancho", "") + " " + seo["descripcion"])
    for c in sel.get("campanas", []):
        R = REGLAS_C.get(c)
        if not R:
            err.append(f"campaña desconocida: {c}")
            continue
        validos = [m for m in miembros if m in {norm(v) for v in R["miembros_validos"]}]
        if len(validos) < R["miembros_min"]:
            err.append(f"{c}: 'miembros' necesita ≥{R['miembros_min']} de {R['miembros_validos']}")
        if R.get("idioma") and idioma != R["idioma"]:
            err.append(f"{c}: idioma {idioma}, tiene que ser {R['idioma']}")
        for h in R["hashtags"] + ([f"#{m}" for m in validos] if R.get("hashtag_por_miembro") else []):
            if norm(h) not in tags_desc:
                err.append(f"{c}: falta el hashtag {h}")
        if not any(norm(m) in texto for m in R["mencionar"]):
            err.append(f"{c}: el título/gancho/descripción tiene que nombrar a {R['mencionar']}")
        cta = sel.get("cta", "")
        if R.get("cta") and not (cta and any(norm(m) in norm(cta) for m in R["mencionar"])):
            err.append(f"{c}: falta 'cta' en seleccion.json que nombre a {R['mencionar']} (p. ej. 'Subscribe to Tomo on YouTube')")
        for t in R.get("en_texto", []):
            if norm(t) not in norm(seo["descripcion"] + " " + cta + " " + sel.get("gancho", "")):
                err.append(f"{c}: '{t}' tiene que salir en pantalla (cta) o en la descripción")
        if R.get("termina") and datetime.now(timezone.utc).date().isoformat() > R["termina"]:
            aviso.append(f"{c}: la campaña terminó el {R['termina']}")

ok = not err
(out / "qa.json").write_text(json.dumps({"ok": ok, "errores": err, "avisos": aviso,
                                         "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds")},
                                        ensure_ascii=False, indent=1), encoding="utf-8")
print(("QA OK" if ok else "QA FALLA") + "".join(f"\n- {e}" for e in err + [f"(aviso) {a}" for a in aviso]))
print(f"hoja de contacto: {(out / 'hoja.jpg').relative_to(RAIZ)}")
sys.exit(0 if ok else 1)
