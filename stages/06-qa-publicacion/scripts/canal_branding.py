"""Pone el banner y la descripción del canal con la API (cuota: ~50 + 50 unidades).
Uso:
  python canal_branding.py banner <imagen.jpg>        # 16:9, mín. 2048x1152, máx. 6 MB
  python canal_branding.py descripcion <texto.txt>
  python canal_branding.py ver                        # muestra descripción y URL del banner actuales
La FOTO DE PERFIL no se puede cambiar por API (YouTube no lo permite): se pone a mano en Studio → Personalización.
"""
import sys
from pathlib import Path

from googleapiclient.http import MediaFileUpload

sys.path.insert(0, str(Path(__file__).parent))
import youtube_api as Y  # noqa: E402


def canal_actual(y):
    c = y.channels().list(part="brandingSettings", mine=True).execute()["items"][0]
    assert c["id"] == Y.CANAL_ID, f"canal inesperado {c['id']}"
    return c


def actualizar(y, cambio):
    c = canal_actual(y)
    bs = c["brandingSettings"]
    for seccion, valores in cambio.items():
        bs.setdefault(seccion, {}).update(valores)
    y.channels().update(part="brandingSettings", body={"id": c["id"], "brandingSettings": bs}).execute()


def main():
    accion = sys.argv[1]
    y = Y.yt()
    if accion == "banner":
        r = y.channelBanners().insert(media_body=MediaFileUpload(sys.argv[2], mimetype="image/jpeg")).execute()
        actualizar(y, {"image": {"bannerExternalUrl": r["url"]}})
        print("ok banner puesto (puede tardar unos minutos en verse)")
    elif accion == "descripcion":
        texto = Path(sys.argv[2]).read_text(encoding="utf-8").strip()
        if len(texto) > 1000:
            sys.exit(f"descripción de {len(texto)} caracteres: máx. 1000")
        actualizar(y, {"channel": {"description": texto}})
        print(f"ok descripción puesta ({len(texto)} caracteres)")
    elif accion == "ver":
        bs = canal_actual(y)["brandingSettings"]
        print("Descripción:", (bs.get("channel", {}).get("description") or "")[:120].replace("\n", " "), "…")
        print("Banner:", bs.get("image", {}).get("bannerExternalUrl", "(ninguno)"))


if __name__ == "__main__":
    main()
