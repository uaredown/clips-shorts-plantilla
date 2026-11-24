# 02 · Selección y gancho (aquí está el APORTE PROPIO)

**Cargar:** `shared/receta-produccion.md` · `../01-fuentes-clips/output/<slug>/fuente.json` · hoja de contacto pequeña de fuente.mp4 (una imagen) · `python ../04-montaje/scripts/variedad_check.py tabla 5` (para no repetir).
**Hacer:** escribir `output/<slug>/seleccion.json` y luego `python scripts/recortar.py <slug>` (valida y genera clip.mp4).
```json
{"streamer": "KaiCenat",  // o "CORE"/"Lacy"/"Clix" · "campanas": ["CORE", "Lacy"] (todas las que cumple; reglas en shared/campanas.json) · "miembros": ["Lacy", "Silky"] (quién sale)
  "plataforma": "twitch", "canal_url": "https://twitch.tv/kaicenat",
 "desde": 3.2, "hasta": 34.0,                      // segundos de fuente.mp4: empezar en el planteamiento, acabar en la reacción
 "momento": "qué pasa, 1 frase",
 "aporte": "contexto/dato propio que añadimos (≥6 palabras): por qué importa",
 "gancho": "≤7 palabras, idioma del clip", "gancho_dur": 2.0,
 "tipo_gancho": "pregunta|cifra|contradiccion|aviso|reaccion|cuenta-atras|contexto",
 "estructura": "setup-reaccion|cold-open|reaccion-replay|cronologico|antes-despues",
 "layout": "stack|split|zoom|blur",   // stack = cara ARRIBA grande + juego abajo (estilo viral por defecto); "juego": [x,y,w,h] recorta el juego en stack/split/blur (quitar chat, contadores y subtítulos quemados)
 "subs_estilo": "palabra|grupo",   // palabra = una palabra gigante en la unión (por defecto con stack)
 "titular": "frase fija todo el vídeo con emojis (Streamer + situación), sustituye al gancho de 2 s",
 "pregunta_en_pantalla": false,   // la pregunta siempre va en la descripción
 "facecam": [x, y, w, h],   // fracciones 0-1 (split); zoom: "centro_x", "zoom", "punch": true (zooms alternos cada ~2,5 s; para "just chatting"/cámara fija)
 "acento": "#FF2E88|#22D3EE|#FACC15|#A3E635|#FB923C", "fuente": "Impact|Bahnschrift|Segoe UI Black", "pos_subs": "centro|bajo",
 "segmentos": [{"desde": 0, "hasta": 28, "vel": 1}, {"desde": 21, "hasta": 24, "vel": 0.6, "etiqueta": "REPLAY"}],  // opcional, s de clip.mp4
 "pregunta": "pregunta final para comentarios, idioma del clip",
 "cta": "solo si la campaña lo exige (Tomo): Subscribe to Tomo on YouTube @Tomovids",
 "bucle": "cómo enlaza el final con el principio",
 "spoiler": false, "musica_con_copyright": false}
```
- `cold-open`: primer segmento = 1-2 s del clímax y luego el clip desde el principio. `reaccion-replay`: clip + repetición lenta del instante clave.
- La variedad la vigila `variedad_check.py` (tipo de gancho, estructura, acento, tipografía, plantilla, streamer, textos parecidos).
**Producir:** `output/<slug>/seleccion.json` + `clip.mp4` (≤59 s final).
