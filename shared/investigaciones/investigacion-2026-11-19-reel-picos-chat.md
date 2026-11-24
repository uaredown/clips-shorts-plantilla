# Reel de referencia: "máquina de clips" por picos de chat (2026-11-19)

Fuente: instagram.com/p/Df5dLv3hw6U (diego.scendit, 18-11-2026, 4.460 likes / 2.254 comentarios). Formato del reel: persona a cámara + gráficos animados; no es material de clips para nosotros, sí el método.

## El método
1. Bajar el VOD **con todo su chat** (TwitchDownloader, gratis y de código abierto; CLI: `TwitchDownloaderCLI chatdownload`).
2. Contar mensajes cada 10 s → donde el chat se dispara hay un momento viral.
3. **El truco:** el chat reacciona después → el clip empieza ~20 s antes del pico.
4. Cortar, poner en vertical y subtitular.

## Por qué nos sirve
- Encuentra momentos de VOD **que nadie ha clipeado** (receta v2: fuente única, sin duplicados).
- No hace falta bajar horas de audio (el 19-11 escanear_vod.py tardó >1 h en solo bajar el audio de 2,5 h).
- Después solo se baja en 1080p60 el tramo elegido (yt-dlp `--download-sections`).

## Bloqueo
Leer el chat necesita una herramienta externa (TwitchDownloaderCLI o chat-downloader): **decisión del usuario** (ya estaba pendiente). La llamada directa a la API de Twitch fue denegada por permisos el 19-11.
