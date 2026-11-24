"""Paquete para SUBIR A MANO en YouTube Studio (cuando la cuota de la API no alcanza). No gasta cuota.
Uso: python paquete_manual.py <short-NNN-slug> "AAAA-MM-DD HH:MM"   (hora UTC a la que programarlo)
Exige qa.json ok y meta.json (preparar_meta.py). Crea en output/_subir_a_mano/<fecha UTC>/:
  "<HH.MM España> - <slug>.mp4"  y  "<HH.MM España> - <slug>.txt" (título, descripción, etiquetas, ajustes, campaña)
y marca output/<slug>/manual.json para que subir_shorts.py no lo suba por API. Cuando el usuario lo suba, apuntar el
enlace con: python paquete_manual.py <slug> --enlace https://youtu.be/xxxx   (lo pasa al registro semanal).
"""
import json
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
PUB = RAIZ / "stages/06-qa-publicacion/output"
sys.path.insert(0, str(Path(__file__).parent))

slug = sys.argv[1]
d = PUB / slug
if "--enlace" in sys.argv:
    import subir_shorts as SS  # noqa: E402
    m = json.loads((d / "manual.json").read_text(encoding="utf-8"))
    url = sys.argv[sys.argv.index("--enlace") + 1]
    vid = url.rstrip("/").split("/")[-1].split("=")[-1]
    cuando = datetime.fromisoformat(m["publicar_en"].replace("Z", "+00:00"))
    meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
    (d / "subido.json").write_text(json.dumps({"id": vid, "url": f"https://youtu.be/{vid}", "publicar_en": m["publicar_en"],
                                               "manual": True}, indent=1), encoding="utf-8")
    f = SS.registrar(slug, meta, vid, cuando)
    print(f"ok apuntado en {f.name}: https://youtu.be/{vid}")
    sys.exit()

qa = json.loads((d / "qa.json").read_text(encoding="utf-8"))
if not qa.get("ok"):
    sys.exit(f"QA no pasado: {qa.get('errores')}")
meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
utc = datetime.strptime(sys.argv[2], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
esp = utc + timedelta(hours=1)  # España en invierno = UTC+1
sel = json.loads((RAIZ / "stages/02-seleccion-gancho/output" / slug / "seleccion.json").read_text(encoding="utf-8"))
camp = sel.get("campanas") or []
carpeta = PUB / "_subir_a_mano" / utc.strftime("%Y-%m-%d")
carpeta.mkdir(parents=True, exist_ok=True)
base = f"{esp:%H.%M} - {slug}"
shutil.copy2(meta["video"], carpeta / f"{base}.mp4")
txt = f"""SUBIR A MANO EN YOUTUBE STUDIO — {slug}
Vídeo: {base}.mp4 (esta misma carpeta)

1) TÍTULO (copiar):
{meta['titulo']}

2) DESCRIPCIÓN (copiar):
{meta['descripcion']}

3) MINIATURA: no hace falta (Short).
4) PÚBLICO: "No, no es contenido para niños".
5) MÁS OPCIONES → Etiquetas (copiar):
{', '.join(meta.get('tags', []))}
   Idioma del vídeo: Inglés · Categoría: Videojuegos · Contenido alterado/sintético: NO
6) VISIBILIDAD → Programar: {esp:%d/%m/%Y %H:%M} (hora de España)  =  {utc:%H:%M} UTC
"""
if camp:
    txt += f"""
7) CAMPAÑA {', '.join(camp)}: cuando se publique, enviar el enlace en Content Rewards
   entre las {esp:%H:%M} y las {esp + timedelta(minutes=30):%H:%M} (hora de España).
"""
txt += f"\nCuando esté subido, dile a Claude el enlace (youtu.be/...) para apuntarlo en el registro.\n"
(carpeta / f"{base}.txt").write_text(txt, encoding="utf-8")
(d / "manual.json").write_text(json.dumps({"publicar_en": utc.strftime("%Y-%m-%dT%H:%M:%SZ"), "carpeta": str(carpeta)},
                                          indent=1), encoding="utf-8")
print(f"ok {carpeta.relative_to(RAIZ)} / {base}.mp4 + .txt · programar {esp:%d/%m %H:%M} España")
