# Estilo de clips de streamers que funcionan (2026-11-18)

5 Shorts de referencia que pasó el usuario (analizados con yt-dlp + una hoja de contacto en `output/_pruebas/referencias/hoja_referencias.jpg`).

| # | canal (subs) | streamer | dur. | vistas | formato |
|---|---|---|---|---|---|
| 1 | trashclips (121K) | Kai Cenat (GTA 5) | 19 s | 974K | **cara ARRIBA / juego ABAJO (50/50)**, subtítulo de 1 palabra en la unión, blanco con palabras clave en rosa |
| 2 | StoryLoop (8) | Speed (tráiler GTA 6) | 21 s | 7,6K | 3 franjas: **titular fijo amarillo arriba** ("SPEED REACTION ON GTA6 TRAILER") sobre fondo difuminado, vídeo en medio, cara abajo |
| 3 | LosPollosTv (141K) | Jynxzi (Kick) | 37 s | 1M | cara arriba con **frase fija entre comillas + emojis**; abajo gameplay "satisfactorio" (rampas de GTA) con cabecera fija y subtítulos de 1 palabra |
| 4 | MrLucho (23K) | Speed | 52 s | **17,6M** | **titular fijo blanco arriba** ("Speed Watching His Own Stream TURNED Into A DISASTER 😭💀") + vídeo centrado sobre fondo difuminado; subtítulos de 2-3 palabras en cian/blanco |
| 5 | Xyro7exe (22K) | Speed (Fortnite) | 20 s | **28,9M** | **cara ARRIBA grande / juego abajo**; **una palabra gigante amarilla** (tipo Impact, contorno negro) en la unión; **efectos de sonido escritos** (*LAUGH*, *BARK*) |

## Patrones comunes
1. **Cara del streamer ARRIBA y grande** (la mitad superior); el juego abajo. Es al revés que nuestro `split` (juego arriba).
2. **Subtítulos de UNA palabra (o 2-3), enormes**, centrados justo en la unión de las dos mitades, con contorno negro grueso. Amarillo o blanco, con palabras clave en color.
3. **Titular fijo durante todo el vídeo** (2 de 5 y el de 17M): una frase que cuenta la situación, con emojis 😭💀. Hace de gancho permanente y de aporte propio.
4. **Efectos de sonido escritos** entre asteriscos (*LAUGH*, *SCREAMS*, *BARK*): se añaden a mano en palabras.json.
5. **Cortos**: 19-52 s; los dos con más vistas duran 20 y 52 s. Sin cartela final ni pregunta en pantalla (la pregunta va en la descripción).
6. **Títulos**: nombre del streamer + situación + palabra en MAYÚSCULAS + emojis ("TURNED Into A DISASTER 😭💀", "Fell in Love with…😂").
7. Lo que NO copiamos: descripciones con listas de 25 streamers que no salen (metadatos engañosos = riesgo de política de spam) y gameplay ajeno de relleno (formato 3; las campañas exigen al streamer como foco).

Fuentes web: [eklipse: plantillas de clips de Twitch](https://blog.eklipse.gg/beginner-guide-2/twitch-clip-templates.html) · [clip.dor.gg: patrón viral de gaming shorts](https://clip.dor.gg/en/blog/gaming-shorts-viral-pattern) · [captions.ai gaming](https://captions.ai/help/use-cases/gaming) · [clipspeed: canales de clips de gaming](https://www.clipspeed.ai/blog/gaming-clip-channels.html)

## Aplicado al pipeline (montar.py)
- Layout nuevo **`stack`**: cara arriba 1080×960 + juego abajo 1080×960.
- **`subs_estilo: "palabra"`**: una palabra gigante en la unión (o en `pos_subs`).
- **`titular`**: texto fijo arriba todo el vídeo (sustituye al gancho de 2 s).
- La pregunta final en pantalla pasa a ser opcional (`pregunta_en_pantalla`); siempre va en la descripción.
