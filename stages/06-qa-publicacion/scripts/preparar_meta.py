"""Genera stages/06-qa-publicacion/output/<slug>/meta.json para youtube_api.py / subir_shorts.py
(plantilla: preparar_meta.py de Cathode Files, 2026-11-17). Exige qa.json ok.
Uso: python preparar_meta.py <short-NNN-slug> [--playlist PLxxxx] [--srt]
--srt sube también final.srt (+400 de cuota; por defecto NO: 5 Shorts x 1.600 = 8.000 caben en 10.000/día).
Lee 05-seo/<slug>/seo.json ({titulo, descripcion, tags, hashtags, idioma?}) y 04-montaje/<slug>/ (final.mp4, final.srt,
montaje.json con el idioma detectado). Playlist por defecto: output/_canal.json {"playlist": "PL..."} (si existe).
publicar_en lo pone subir_shorts.py al subir (siguiente hueco libre).
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
PUB = RAIZ / "stages/06-qa-publicacion/output"
slug = sys.argv[1]
qa = json.loads((PUB / slug / "qa.json").read_text(encoding="utf-8")) if (PUB / slug / "qa.json").exists() else {}
if not qa.get("ok"):
    sys.exit(f"ERROR: QA no pasado ({qa.get('errores', 'sin qa.json')})")
playlist = sys.argv[sys.argv.index("--playlist") + 1] if "--playlist" in sys.argv else None
if not playlist and (PUB / "_canal.json").exists():
    playlist = json.loads((PUB / "_canal.json").read_text(encoding="utf-8")).get("playlist")

d04 = RAIZ / "stages/04-montaje/output" / slug
seo = json.loads((RAIZ / "stages/05-seo/output" / slug / "seo.json").read_text(encoding="utf-8"))
mont = json.loads((d04 / "montaje.json").read_text(encoding="utf-8"))
desc = seo["descripcion"].strip()
falta_hash = [h for h in seo.get("hashtags", []) if h.lower() not in desc.lower()]
if falta_hash:
    desc += "\n\n" + " ".join(falta_hash)
meta = {"video": str(d04 / "final.mp4"), "titulo": seo["titulo"].strip(),
        "descripcion": desc, "tags": seo.get("tags", []), "idioma": seo.get("idioma") or mont["idioma"],
        "categoria": "20", "sintetico": bool(seo.get("sintetico", False))}
if "--srt" in sys.argv:
    meta["srt"] = str(d04 / "final.srt")
if playlist:
    meta["playlist"] = playlist
if len(meta["titulo"]) > 100 or len(meta["descripcion"]) > 5000 or sum(len(t) for t in meta["tags"]) > 450:
    sys.exit("ERROR: título >100, descripción >5000 o tags demasiado largas")
(PUB / slug).mkdir(parents=True, exist_ok=True)
(PUB / slug / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"ok meta.json | {meta['titulo']} | idioma {meta['idioma']} | playlist {playlist or 'NINGUNA'}")
