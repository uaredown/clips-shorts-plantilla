# Lecciones del canal original (GTA 6, nov. 2026)

Lo que funcionó, lo que no y las trampas encontradas. Úsalas como punto de partida, no como verdad absoluta: cámbialas con datos de tu canal.

## Contenido
- **No uses los clips top de Twitch/YouTube**: los suben cientos de clippers y YouTube agrupa los duplicados → 1-40 vistas. Con **fuente propia** (grabar el directo con `clipper_vivo.py` o momentos de VOD sin clip) los Shorts pasaron a **~1.100-1.500 vistas** cada uno.
- **Nombres grandes rompen el techo** (Speed: 2.400 vistas), pero si hay una campaña con más de 1.000 clippers del mismo streamer, el contenido se satura y puede quedarse en 0.
- **12-25 s**; el fotograma 1 es la acción (cold-open del clímax), no una cara quieta ni un menú.
- Estilo que mejor funcionó: **`stack`** (cara del streamer arriba, juego abajo), **subtítulos de una palabra gigante**, **titular fijo** con 1-2 emojis ("Streamer + situación").
- Descartar siempre: cinemáticas de historia y finales (spoilers), desnudos, clubs de estriptis, tramos sexuales del chat, música con copyright, pantallas de menú/mapa, escenas demasiado oscuras.
- **Comprobar el audio**: Twitch silencia trozos de VOD con música (audio a 2 kb/s). Medir con `ffmpeg -af volumedetect` antes de montar.
- Whisper con VAD se come la voz cuando hay mucho ruido de juego → `transcribir.py --sin-vad`. Quitar de los subtítulos los diálogos que el juego ya subtitula y las palabras mal oídas; añadir a mano la frase clave si falta.
- Suscriptores: los canales de clips convierten muy poco (4 subs con 15k vistas). Probar CTA final y pregunta en pantalla en A/B.

## Picos de chat (cómo encontrar momentos)
- El chat reacciona tarde: el clip empieza **~20-25 s antes** del pico.
- Las reacciones (LMAO, 😭, 💀, WTF, CLIP, NOOO) pesan más que los mensajes normales; los sorteos ("1", "!enter") y los tramos sexuales no cuentan.
- Los mayores picos a veces son cosas que no sirven (club, sorteos, charla): **mirar siempre la hoja de contacto**.
- No lanzar más de **2 clippers en vivo a la vez**: con 4 el PC se quedó sin memoria y quedaron procesos ffmpeg huérfanos de 1 GB.

## YouTube y la API
- Subir siempre como **privado programado** (publishAt) y verificarlo.
- Canal **sin verificar** → límite de ~4-5 subidas/día (`uploadLimitExceeded`). Verificar el canal el primer día.
- Cuota 10.000/día ≈ 5-6 subidas sin subtítulos .srt ni playlists. Se renueva hacia las 08:00 UTC.
- Token OAuth en modo prueba: caduca cada ~7 días.
- Analytics (retención, % visto) llega con 2-3 días de retraso; las impresiones y "visto vs. deslizado" solo en Studio.
- Marcar siempre "no es para niños" y "sin promoción pagada".

## Campañas de clipping (Content Rewards y similares)
- Es el dinero real al principio: la monetización de YouTube (YPP) pide 500 subs + 3M vistas en 90 días (sin anuncios) o 1.000 + 10M (20M desde feb. 2027), y rechaza canales de clips sin aporte propio claro.
- Cada campaña tiene reglas: hashtag obligatorio, el streamer como protagonista, sin logos, mínimo de vistas por clip (500-1.000) y bolsa total.
- **Enviar en los 30 min** siguientes a publicar: un envío a los 34 min se rechazó. Si automatizas recordatorios, que sean de una sola vez y a la hora y 01, no recurrentes (llegan tarde).

## Forma de trabajar con Claude Code
- Una receta corta (`shared/receta-produccion.md`) + un `CONTEXT.md` por etapa: así cada Short gasta pocos tokens.
- Producir **por tandas** y dejarlas programadas; nada de bucles continuos.
- `variedad_check.py` bloquea repeticiones (mismo gancho, color, tipografía, pregunta parecida, >3 seguidos del mismo streamer): cambiar la selección, no forzar.
- Calidad antes que volumen: si el material del día es flojo, mejor 3 buenos que 5 malos.
