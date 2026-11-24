# 01 · Fuentes de clips

**Cargar:** `shared/permisos-streamers.md` (solo la tabla). Nada más.
**Hacer:**
1. Elegir streamer con estado `ok` (si no hay ninguno, conseguir permisos: ver la tabla; preguntar al usuario solo si hay que escribirle a alguien en su nombre).
2. `python scripts/buscar_clips.py <streamer> [--plataforma kick] [--rango 24hr]` → top de clips (para momentos de VOD/YouTube, usar la URL directa).
3. `python scripts/descargar_clip.py <short-NNN-slug> <url> --streamer <s> [--desde hh:mm:ss --hasta hh:mm:ss]`
   - Slug: `short-NNN-streamer-momento` (NNN = siguiente número libre, 3 cifras). Pruebas: `--prueba` y número 000.
- **CORE** (campaña, shared/campanas.md): buscar en los Twitch de lacy, silky, jasontheween, adapt, marlon, stableronaldo; descargar con `--streamer CORE` solo si salen **≥2 miembros**. No usar vídeos del canal de YouTube de CORE.
- **Directo en vivo:** `--directo 150` graba 150 s desde ahora. Ojo: pueden salir **anuncios de Twitch** ("Commercial break in progress") al principio y **música** de fondo → mirar la hoja de contacto + transcripción y cortar fuera. Grabar de más (150-180 s) y elegir en 02.
- YouTube (Tomo, Speed): el script ya pasa `--js-runtimes node` (sin eso faltan formatos).
- **Momentos de VOD por picos de chat** (receta v2, fuente única): `python scripts/picos_chat.py <url VOD> --top 10` (TwitchDownloaderCLI en bin/, ~3 min por 8 h; solo capítulos de GTA, solo reacciones, quita sorteos y tramos sexuales) → cribar en 480p y bajar solo el bueno con `descargar_clip.py --desde/--hasta`. Siempre mirar la hoja: el chat también se ríe de clubs, paneles y charla.
- **Clipper en vivo** (2026-11-20, idea de un reel): `python scripts/clipper_vivo.py <canal> --minutos 60` graba con Streamlink (sin anuncios) y corta solo 25 s antes + 10 s después de cada pico de chat → `output/_vivo/<canal>/` + picos.txt. Llega antes que el VOD y que los demás clippers. Revisar la hoja (¿GTA? ¿sin club?). Más clips: `--umbral 2`.
- **Recopilación** (receta v2): `python scripts/recopilar.py <slug>` con `output/<slug>/recopilacion.json` (3-4 partes de grabaciones propias) → fuente vertical; en 02 usar `"layout": "zoom"` y `"creditos": [...]`.
**Producir:** `output/<slug>/fuente.mp4` + `fuente.json` (url, streamer, permiso, título y vistas originales).
**Reglas:** nada antes del desbloqueo oficial (19-11-2026 00:00 de cada región), ni filtraciones, ni cinemáticas de historia/finales, ni clips con música comercial de fondo. Preferir momentos de gameplay emergente + reacción. Mid-tier tiene menos competencia que Kai/Speed.
