"""Conexión con la YouTube Data API v3 (subir y programar los Shorts del canal tu canal).
Copiado de Cathode Files (que lo copió de Bow Tie Mind) el 2026-11-17 y parametrizado: idioma POR SHORT, categoría 20,
containsSyntheticMedia por Short, puerto 8082 y comando verificar.

Uso:
  python youtube_api.py auth                  # autoriza (abre el navegador; entrar con la cuenta del canal) y guarda token.json
  python youtube_api.py canal                 # muestra el canal conectado (¡comprobar que es tu canal!)
  python youtube_api.py subir <meta.json>     # sube un vídeo según un json (ver abajo)
  python youtube_api.py verificar <id> [publishAt]   # comprueba privado + publishAt
  python youtube_api.py prueba                # prueba completa: sube un clip privado de 5 s con subtítulos y lo borra

meta.json:
  {"video": "ruta/final.mp4", "titulo": "...", "descripcion": "...", "tags": ["..."],
   "idioma": "en" (idioma del clip: audio, metadatos y subtítulos), "srt": "ruta/final.srt" (opcional),
   "miniatura": "ruta.jpg" (opcional), "publicar_en": "2026-11-20T17:00:00Z" (opcional: si falta queda privado),
   "playlist": "PLxxxx" (opcional), "categoria": "20", "sintetico": false (true si hay voz/imagen de IA)}

Credenciales en ../credenciales/ (client_secret.json del cliente OAuth "Aplicación web" con la URI de redirección
http://localhost:8082/ ; token.json se crea solo). NUNCA copiar token.json de otro proyecto (subiría a otro canal).
Cuota aprox.: insert 1.600 · captions 400 · thumbnails 50 · playlistItems 50.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError  # noqa: F401
from googleapiclient.http import MediaFileUpload

CRED = Path(__file__).resolve().parents[1] / "credenciales"
SECRET = CRED / "client_secret.json"
TOKEN = CRED / "token.json"
PUERTO = 8082  # 8080 lo usan Bow Tie Mind y Cathode Files
CANAL_ID = "PON_AQUI_EL_ID_DE_TU_CANAL"  # youtube.com/account_advanced → ID del canal (empieza por UC)
IDIOMAS = {"en": "English", "es": "Español", "fr": "Français", "pt": "Português", "de": "Deutsch", "it": "Italiano",
           "ar": "العربية", "tr": "Türkçe", "pl": "Polski", "ru": "Русский", "ja": "日本語", "ko": "한국어"}
SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.force-ssl",
          "https://www.googleapis.com/auth/yt-analytics.readonly"]


def credenciales(interactivo=False):
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES) if TOKEN.exists() else None
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception:  # refresh token caducado/revocado (app en modo prueba: 7 días) → pedir login otra vez
            creds = None
    if not creds or not creds.valid:
        if not interactivo:
            sys.exit("Sin token válido (invalid_grant / caducado): ejecuta  python youtube_api.py auth")
        flow = InstalledAppFlow.from_client_secrets_file(str(SECRET), SCOPES)
        creds = flow.run_local_server(port=PUERTO, access_type="offline", prompt="consent", open_browser=True)
    TOKEN.write_text(creds.to_json(), encoding="utf-8")
    return creds


def yt():
    return build("youtube", "v3", credentials=credenciales())


def canal():
    r = yt().channels().list(part="snippet,statistics,status", mine=True).execute()
    for c in r.get("items", []):
        print(f"Canal: {c['snippet']['title']} ({c['id']})")
        print(f"Suscriptores: {c['statistics'].get('subscriberCount')} · vídeos: {c['statistics'].get('videoCount')}")
        print(f"Estado: {c.get('status', {})}")
        if c["id"] != CANAL_ID:
            print(f"¡AVISO! No es el canal esperado ({CANAL_ID}). Relanza auth y elige el canal correcto.")
    return r


def subir(meta):
    y = yt()
    idioma = meta.get("idioma", "en")
    status = {"privacyStatus": "private", "selfDeclaredMadeForKids": False,
              "containsSyntheticMedia": bool(meta.get("sintetico", False))}
    if meta.get("publicar_en"):
        status["publishAt"] = meta["publicar_en"]
    body = {"snippet": {"title": meta["titulo"], "description": meta.get("descripcion", ""),
                        "tags": meta.get("tags", []), "categoryId": meta.get("categoria", "20"),
                        "defaultLanguage": idioma, "defaultAudioLanguage": idioma},
            "status": status, "paidProductPlacementDetails": {"hasPaidProductPlacement": False}}  # ni niños ni pagado
    media = MediaFileUpload(meta["video"], chunksize=8 * 1024 * 1024, resumable=True)
    req = y.videos().insert(part="snippet,status,paidProductPlacementDetails", body=body, media_body=media)
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    vid = resp["id"]
    print(f"Vídeo subido: https://youtu.be/{vid}  (estado: {resp['status'].get('privacyStatus')} "
          f"publishAt {resp['status'].get('publishAt')})")
    if meta.get("miniatura"):
        for n in range(6):  # justo tras subir, thumbnails.set puede dar 403 → reintentar cada minuto
            try:
                y.thumbnails().set(videoId=vid, media_body=MediaFileUpload(meta["miniatura"])).execute()
                print("  miniatura puesta")
                break
            except Exception as e:  # noqa: BLE001
                if n == 5:
                    print(f"  miniatura NO puesta ({str(e)[:80]}); ¿falta verificar el canal en youtube.com/verify?")
                    break
                time.sleep(60)
    if meta.get("srt"):
        y.captions().insert(part="snippet",
                            body={"snippet": {"videoId": vid, "language": idioma, "name": IDIOMAS.get(idioma, idioma),
                                              "isDraft": False}},
                            media_body=MediaFileUpload(meta["srt"], mimetype="application/octet-stream")).execute()
        print("  subtítulos subidos")
    if meta.get("playlist"):  # tarda ~1 min en verse: NO repetir (se duplica)
        y.playlistItems().insert(part="snippet", body={"snippet": {
            "playlistId": meta["playlist"], "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
        print("  añadido a la playlist")
    return vid


def verificar(vid, publish_at=None):
    it = yt().videos().list(part="status,snippet", id=vid).execute()["items"]
    if not it:
        print(f"{vid}: NO EXISTE")
        return False
    st = it[0]["status"]
    ok = st["privacyStatus"] == "private" and (not publish_at or st.get("publishAt", "").startswith(publish_at[:16]))
    print(f"{vid}: {st['privacyStatus']} · publishAt {st.get('publishAt')} · upload {st.get('uploadStatus')} · "
          f"{'OK' if ok else 'REVISAR'}")
    return ok


def prueba():
    """Prueba de extremo a extremo con un vídeo vertical privado de 5 s que se borra al final (~2.050 unidades)."""
    tmp = CRED.parent / "output" / "_prueba_api"
    tmp.mkdir(parents=True, exist_ok=True)
    mp4, srt = tmp / "prueba.mp4", tmp / "prueba.srt"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=white:s=1080x1920:d=5",
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(mp4)], check=True)
    srt.write_text("1\n00:00:00,000 --> 00:00:04,000\nAPI test\n", encoding="utf-8")
    print("1) Canal conectado:")
    canal()
    print("2) Subida de prueba (privada) + subtítulos:")
    vid = subir({"video": str(mp4), "titulo": "API test (borrar)", "descripcion": "Prueba automática", "srt": str(srt)})
    print("3) Lectura del vídeo subido:")
    verificar(vid)
    print("4) Borrado del vídeo de prueba:")
    yt().videos().delete(id=vid).execute()
    for f in (mp4, srt):
        f.unlink(missing_ok=True)
    print("  borrado. PRUEBA COMPLETA OK")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "canal"
    if cmd == "auth":
        credenciales(interactivo=True)
        print("Autorizado. Token guardado en", TOKEN)
        canal()
    elif cmd == "canal":
        canal()
    elif cmd == "subir":
        subir(json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")))
    elif cmd == "verificar":
        verificar(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == "prueba":
        prueba()
