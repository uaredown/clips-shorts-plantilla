# Mejoras de clips: herramientas abiertas, foros y guías (2026-11-18)

## Cómo encuentran los momentos virales (GitHub)
- [Stream Clipper](https://github.com/nirvagold/stream-clipper): picos de audio + actividad del chat, 10-50x más rápido que tiempo real.
- [Twitch Highlight Finder](https://github.imc.re/hougesen/twitch-highlight-finder), [24th de highlighter](https://github.com/YBIGTA/24th-de-highlighter), [CTIC clipper](https://github.com/josec07/clipper), [Chat Analyzer](https://chat-analyzer.readthedocs.io/): **densidad de mensajes del chat por segundo** con media móvil → los picos son los momentos.
- Nosotros ya tenemos: heatmap de YouTube (momentos_youtube.py), clips creados por el chat de Twitch (buscar_clips.py), volumen + palabras de reacción (escanear_vod.py). **Falta: picos del chat** (necesita instalar `chat-downloader`; la instalación la bloqueó el sistema de permisos → decisión del usuario).

## Guía específica de GTA 6 ([clipspeed](https://clipspeed.ai/gta6/gta-6-shorts-strategy.html))
- Abrir en el fotograma más intenso (choque, revelación o cara de reacción). Si lo mejor llega a los 20 s, **empezar por ahí**.
- Texto del gancho que plantee una pregunta o promesa: "Wait for the ending", "This shouldn't be possible".
- Títulos con **riesgo** ("He almost lost it all in GTA 6"), **superlativo** ("The craziest thing…") o **hueco de curiosidad** ("Nobody expected GTA 6 to let you do this"). Nunca solo describir: prometer reacción o resultado.
- Momentos de la semana de lanzamiento: primeras reacciones al cargar, caos sandbox (persecuciones, acrobacias, explosiones, físicas rotas), "¿ha pasado eso de verdad?", emoción real (rabia, incredulidad, ataques de risa, sustos).
- Señales: compartidos/guardados = la más fuerte; deslizar al instante = falla el primer fotograma o el texto.
- Errores: volumen sin filtrar ganchos; subtítulos sin estilo; publicar a rachas.

## Foros / guías de clippers ([autoclip](https://autoclip.dev/blog/how-youtube-shorts-algorithm-treats-clipper-content), [opus](https://www.opus.pro/blog/video-editing-tips), [dev.to](https://dev.to/clamper_ai/how-to-get-more-views-on-youtube-shorts-in-2026-10-proven-tactics-3p9l))
- La retención se mide sobre la duración total: 30 s con 90 % > 60 s con 50 % → **cortar más**.
- Un cambio visual cada ≤3 s; efectos de sonido pocos y en el momento justo.
- Lo que no aplicamos: TikTok/Reels (el usuario solo quiere YouTube Shorts).
