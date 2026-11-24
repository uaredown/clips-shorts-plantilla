# Plantilla: canal de YouTube Shorts con clips de streamers

Todo lo necesario para montar un canal de Shorts que recorta los mejores momentos de streamers (Twitch/YouTube), les añade subtítulos y un titular, y los sube programados por la API de YouTube. Pensado para trabajar con **Claude Code**: cada etapa tiene su `CONTEXT.md` con las instrucciones, y los scripts hacen el trabajo repetitivo.

Sacado de un canal real (clips de GTA 6, noviembre de 2026). Las lecciones de ese canal están en [`docs/lecciones.md`](docs/lecciones.md) y las investigaciones en [`shared/investigaciones/`](shared/investigaciones/).

## Cómo funciona

```
01-fuentes-clips → 02-seleccion-gancho → 03-transcripcion-subs → 04-montaje → 05-seo → 06-qa-publicacion
```

- **La carpeta es la arquitectura**: cada etapa en `stages/0N-nombre/` con su `CONTEXT.md`, sus `scripts/` y su `output/`. El output de una etapa es el input de la siguiente.
- **Mismo nombre (slug) en todas las etapas**: `short-NNN-streamer-momento`.
- **Sin orquestadores**: Claude Code lee la receta y el `CONTEXT.md` de la etapa y ejecuta sus scripts.

| Etapa | Qué hace | Scripts clave |
|---|---|---|
| 01 fuentes | Encuentra y descarga momentos | `quien_en_directo.py`, `clipper_vivo.py` (graba el directo y corta en los picos de chat), `picos_chat.py` (picos de chat de un VOD), `descargar_clip.py` |
| 02 selección | Elige el tramo, gancho, titular y layout | `recortar.py` |
| 03 subtítulos | Transcribe con Whisper local (gratis) | `transcribir.py` (`--sin-vad` si hay mucho ruido de juego) |
| 04 montaje | Vertical 1080×1920, cara + juego, subtítulos palabra a palabra | `montar.py`, `variedad_check.py` |
| 05 SEO | Título, descripción, tags | (a mano, `seo.json`) |
| 06 QA y subida | Comprueba todo y sube como privado programado | `qa.py`, `preparar_meta.py`, `subir_shorts.py`, `youtube_api.py`, `estadisticas.py` |

## Requisitos

- **Windows 10/11** (los scripts usan PowerShell/Git Bash y tareas programadas de Windows; en Mac/Linux funcionan casi todos cambiando el `.bat` por cron).
- **Python 3.10+**, **ffmpeg**, **yt-dlp**, **Streamlink**, **TwitchDownloaderCLI** (para el chat de los VODs).
- **Claude Code** (recomendado) para seguir las etapas.
- Una **cuenta de Google** para el canal y un **proyecto de Google Cloud** (gratis) para la API.

## Puesta en marcha (paso a paso)

### 1. Instalar
```powershell
git clone https://github.com/<tu-usuario>/clips-shorts-plantilla.git
cd clips-shorts-plantilla
powershell -ExecutionPolicy Bypass -File instalar.ps1
```
Instala las librerías de Python (`requirements.txt`), ffmpeg y yt-dlp con winget, Streamlink y descarga TwitchDownloaderCLI en `stages/01-fuentes-clips/bin/`.

### 2. Crear el canal de YouTube
1. Crea el canal (mejor una **cuenta de marca**) con nombre, foto y banner.
2. **Verifica el canal** en youtube.com/verify (teléfono). Sin verificar, YouTube limita las subidas diarias (~4-5) y no deja poner miniaturas.
3. Copia el **ID del canal** (youtube.com/account_advanced, empieza por `UC`) en `CANAL_ID` dentro de `stages/06-qa-publicacion/scripts/youtube_api.py`.

### 3. Conectar la API de YouTube
1. En console.cloud.google.com crea un proyecto y activa **YouTube Data API v3**.
2. Pantalla de consentimiento OAuth: tipo "Externo", añade tu cuenta como usuario de prueba.
3. Credenciales → **ID de cliente OAuth → Aplicación de escritorio** → descarga el JSON como `stages/06-qa-publicacion/credenciales/client_secret.json`.
4. `cd stages/06-qa-publicacion/scripts && python youtube_api.py auth` → inicia sesión y **elige el canal correcto**. Comprueba con `python youtube_api.py canal`.
5. Cuota gratis: 10.000 unidades/día ≈ 5-6 subidas (cada una ~1.600). Para más, pide ampliación de cuota a Google (formulario de auditoría).
6. Ojo: con la app en modo "prueba" el token caduca cada ~7 días (`invalid_grant`) → repetir `auth`.

### 4. Elegir nicho, streamers y campañas
- `shared/streamers.json`: los streamers a vigilar (Twitch/YouTube y prioridad). Viene con un ejemplo real.
- `shared/permisos-streamers.md`: **fuente de verdad** de permisos. Solo se clipea a quien esté en `ok` (o `riesgo`, si decides asumirlo). `descargar_clip.py` lo comprueba.
- `shared/campanas.json` + `campanas.md`: reglas de las campañas de clipping (hashtags, menciones, ≥N vistas por clip). `qa.py` las comprueba.
  - Las campañas de pago por vistas están en plataformas como **Content Rewards** (Reach, Clipping Nation, Clipped & Shipped…). Normalmente hay que **enviar el enlace en los 30 min siguientes a publicar**.
- `shared/marca.md`: nombre, tono, colores y tipografías del canal.
- `shared/receta-produccion.md`: **la receta** (qué clip vale, gancho, duración, SEO). Es lo único que hay que leer para hacer un Short. Adáptala a tu juego.

### 5. Hacer el primer Short
Con Claude Code abierto en la carpeta: *"haz un Short de <streamer>"*. A mano:
```bash
cd stages/01-fuentes-clips/scripts
python quien_en_directo.py
python clipper_vivo.py <canal_twitch> --minutos 45     # máx. 2 a la vez (memoria)
# o desde un VOD: python picos_chat.py <url VOD> --top 15 → descargar_clip.py <slug> <url> --desde .. --hasta ..
# 02: escribir output/<slug>/seleccion.json  → python recortar.py <slug>
# 03: python transcribir.py <slug> [--sin-vad] → corregir palabras.json
# 04: python montar.py <slug>
# 05: escribir output/<slug>/seo.json
# 06: python qa.py <slug> → python preparar_meta.py <slug> → python subir_shorts.py subir 1
```

### 6. Automatizar la subida
`subir_shorts.py` sube como **privado programado** (publishAt) y lo verifica. Para subir sin tener Claude abierto, crea una tarea de Windows que ejecute:
```
subir_programado.bat "13:00,16:00,18:00,20:00,22:30" 5
```
(horas UTC de los huecos y cuántos subir). La cuota y el límite diario se renuevan hacia las 08:00 UTC.

## Reglas que no se saltan
Permiso del streamer · aporte propio (titular, recorte, subtítulos, reencuadre) · ≤59 s (mejor 15-30) · sin spoilers ni filtraciones · sin desnudos, clubs de estriptis ni música con copyright · `variedad_check` · QA antes de subir.

## Qué NO está en este repo
Credenciales y tokens, vídeos, registros y métricas del canal original. Nunca subas `credenciales/` (ya está en `.gitignore`).
