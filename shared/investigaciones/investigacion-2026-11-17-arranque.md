# Investigación de arranque (2026-11-17)

Canal de **clips de streamers jugando GTA 6** en Shorts, en el idioma de cada clip. Búsqueda web del 2026-11-17.

## 1. Fechas (comprobadas)
- **GTA VI sale el jueves 19-11-2026**, 00:00 hora local de cada región, PS5 y Xbox Series X|S. Sin fecha de PC. Precarga abierta desde el 10-11. ([xbox.com](https://www.xbox.com/en-US/games/grand-theft-auto-vi), [Forbes](https://www.forbes.com/sites/brianmazique/2026/05/12/grand-theft-auto-6-release-date-and-everything-confirmed/), [allthings.how](https://allthings.how/gta-6-release-date/))
- Como sale a medianoche local, **Oceanía/Asia desbloquean horas antes que EE. UU.** → los primeros directos empiezan el 18-11 por la tarde-noche (UTC).
- Streamers anunciados: **Kai Cenat** (18-11, 20:00 ET = 19-11 01:00 UTC, partida al 100 %), **IShowSpeed** (YouTube + Twitch, 18-11 21:00 ET = 02:00 UTC; directos de 10-12 h diarios, sin maratón 24 h), **Ludwig**, casa de streamers CORE en Miami, **DDG**, **Michou** (FR). ([TechTimes](https://www.techtimes.com/articles/330968/20261117/ishowspeed-gta-6-stream-starts-3-hours-before-us-unlock-plans-10-12-hour-days-no-marathon.htm), [Sportskeeda](https://www.sportskeeda.com/us/streamers/list-streamers-will-play-gta-6-marathon-livestream), [TheLoadout](https://theloadout.com/kai-cenat-and-ludwig-wont-sleep-when-gta-6-drops))

## 2. Rockstar / Take-Two ([política oficial](https://support.rockstargames.com/articles/200153756/rockstar-games-video-policy), act. ene-2025; [resumen tbreak](https://tbreak.com/gta-6-spoilers-rockstar-video-takedown-policy/))
- Permite subir gameplay, pero la permisión general es para uso **"no comercial"** → monetizar queda a su discreción (pueden reclamar/quitar "en cualquier momento"). Content ID de Take-Two probable → reclamaciones (no strikes) en clips ≤60 s.
- **Retiran:** filtraciones/pre-lanzamiento (cualquier cosa antes del 19-11 local), **finales, cinemáticas aisladas o recopilaciones de cinemáticas, grandes giros de la historia**, programas de TV del juego sueltos, trampas/mods.
- **Consecuencia para nosotros:** clips de **reacciones y gameplay emergente** (caos, físicas, fallos, sustos, risas), **nunca cinemáticas de historia ni spoilers**. Nada antes del desbloqueo oficial.

## 3. YouTube
- **Contenido reutilizado** ([vidIQ](https://vidiq.com/blog/post/youtube-reused-content-policy-guide/)): clips/compilaciones son monetizables **solo si aportamos valor propio** (contexto, edición, comentario). Aplica **aunque el streamer dé permiso**.
- **Contenido no auténtico** (renombrado el 15-07-2025, ampliado jul-2026, [Tubefilter](https://www.tubefilter.com/2026/07/13/youtube-inauthentic-content-monetization-policy-update/)): lo producido en masa con plantilla casi idéntica no se monetiza → **variedad obligatoria** (variedad_check.py).
- **Shorts de 1 a 3 min con cualquier reclamación de Content ID quedan bloqueados en todo el mundo** ([ayuda YouTube](https://support.google.com/youtube/answer/15424877)) → **máx. 59 s**.
- Strikes de copyright (retirada manual por parte de un streamer): 3 = canal eliminado. Los reclamos de Content ID no son strikes.
- **API:** los vídeos subidos con `videos.insert` desde **proyectos de Cloud sin auditar creados después del 28-07-2020 quedan bloqueados en privado** y no se pueden recurrir ([docs videos](https://developers.google.cn/youtube/v3/docs/videos?hl=en)). Hay que confirmar si el proyecto nuevo publica de verdad (ver decisiones.md).

## 4. Clipear streamers ([clipspeed: copyright](https://www.clipspeed.ai/blog/can-you-clip-someone-elses-stream.html), [clipspeed: guía 2026](https://www.clipspeed.ai/blog/clipping-twitch-streamers-youtube-shorts.html), [autoclip Kick](https://autoclip.dev/blog/kick-clip-channel-monetization-2026))
- El directo tiene copyright del streamer. **Lo que hace segura la operación: permiso** (política pública de "clips permitidos", programa de clipping, canal de clips oficial, o permiso directo), **crédito con enlace**, transformación y **retirar al momento si lo piden**. Kick tiene programa de clipping pagado y la mayoría de sus streamers lo fomentan.
- Música de fondo del directo = reclamaciones de Content ID más rápidas → evitar clips con música comercial sonando.
- Momentos: streamers expresivos, momentos que se entienden sin sonido; **mid-tier (5k-50k espectadores) tiene menos competencia** que Kai/Speed (donde habrá cientos de canales de clips).
- Duración: 20-40 s (mediana 30,8 s). Empezar en la frase que plantea la situación, terminar en la reacción (no volver al chat).
- Formato vertical: gameplay arriba + facecam abajo (split), o recorte centrado en la cara para reacciones; fondo difuminado para momentos mixtos.
- Subtítulos gaming: grandes, con contorno/brillo, que no tapen la interfaz del juego; palabra a palabra con color de acento.
- Títulos: **nombre del streamer + el momento concreto**, emocional, <70 caracteres. Hashtags: streamer + juego (#GTA6 #GTAVI) + #shorts.
- Frecuencia en canales que compiten: 3-5 al día, **repartidos**, publicar durante el directo o justo después.
- Lo que hunde: música con copyright, inundar con clips mediocres, malos encuadres, subtítulos desincronizados.

## 5. Retención en Shorts ([bytecap](https://www.bytecap.io/research/youtube-shorts-retention-benchmarks), [creatoressentials](https://www.creatoressentials.com/glossary/viewed-vs-swiped-away/))
- **"Visto vs. deslizado"** = nota del gancho. Objetivo **≥70 % visto** (<60 % malo; >80 % excelente). YouTube no publica cifras oficiales: compararse con uno mismo.
- Gancho en el segundo 0-1 (imagen + texto), cambio visual cada 1-2 s, subtítulos quemados, final que enlace con el principio (bucle) y pregunta para comentarios.

## 6. Horas ([postfa.st, 6.175 posts](https://postfa.st/blog/best-time-to-post-on-youtube), [bytecap](https://www.bytecap.io/research/best-time-to-post-youtube-shorts))
- Sin datos propios: **17:00-20:00 UTC**; fines de semana mejor. Gaming: 15-18 h locales. En lanzamiento manda la **novedad**: subir lo antes posible tras el momento. Luego ajustar con Studio ("cuándo están tus espectadores").

## 7. Receta que sale de aquí → `shared/receta-produccion.md` v1
