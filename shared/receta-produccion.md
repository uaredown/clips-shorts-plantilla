# Receta de producción v1 (2026-11-17) — lo único que hay que leer para hacer un Short

> **v3 (2026-11-21, datos: shared/investigaciones/investigacion-2026-11-21-monetizacion.md). Manda sobre v2:**
> 1. Con v2 cada Short hace ~1,2k vistas; los nombres grandes (Speed 2,4k) rompen el techo → **Speed/Kai y streamers con campaña primero** (sin spoilers del final).
> 2. Test A/B 3 días: en la mitad `cta: "Follow for daily GTA 6 chaos 🦎"` y `pregunta_en_pantalla: true` → comparar subs y comentarios por 1.000 vistas.
> 3. Envío a campañas en ≤30 min, con aviso único a y 01.

> **v2 (2026-11-19, sin vistas desde el lanzamiento → shared/investigaciones/investigacion-2026-11-19-sin-vistas.md). Manda sobre lo de abajo:**
> 1. **Nada de los clips top de Twitch/YouTube** (los suben cientos de clippers y YouTube agrupa duplicados). Fuente: directo grabado (`--directo 300`) o momento de VOD sin clip.
> 2. **12-25 s**. Fotograma 1 = la acción a pantalla completa (cold-open del clímax), no la cara ni la caja del titular.
> 3. Formato fuerte: **recopilación de 3-4 momentos de un tema** (NPC, policía, físicas) de streamers ok → original y con más retención.

Base: `shared/investigaciones/investigacion-2026-11-17-arranque.md`. Cambiar solo con datos (`shared/metricas-canal.md`).

## Campañas
Si el clip es de una campaña (hoy: **CORE**, ≥2 miembros), cumplir `shared/campanas.md`: inglés, #CORE + hashtag por miembro, nombrarlos, nada negativo, sin logos.

## Qué clip vale
- Streamer con permiso `ok` (shared/permisos-streamers.md). Momento que se entiende **sin sonido** y en 1 s.
- Gameplay emergente + reacción: caos, físicas, fallos, sustos, persecuciones, NPC absurdos, risas. **Nunca** cinemáticas de historia, finales ni giros (Rockstar los retira). Nada de música comercial de fondo.
- En lanzamiento (19-11 → primeras 2 semanas) manda la rapidez: momento de hoy, subido hoy.

## Estilo principal (desde 2026-11-18, referencias del usuario de 1M-29M vistas: shared/investigaciones/investigacion-2026-11-18-estilo-referencias.md)
- Gameplay con facecam → **`stack`**: cara del streamer ARRIBA y grande, juego abajo; `centro_x` del juego sin que entre el chat.
- **`subs_estilo: "palabra"`**: una palabra gigante en la unión, contorno negro; efectos de sonido escritos a mano en palabras.json (*LAUGH*, *SCREAMS*).
- **`titular`** fijo arriba: "Streamer + situación" con 1-2 emojis (los emojis salen en blanco y negro en pantalla; en el título de YouTube sí en color).
- 19-40 s (las de más vistas: 20 y 52 s). Pregunta solo en la descripción (`pregunta_en_pantalla: false`).
- Cámara fija sin juego → `zoom` + `punch`. Variedad: rotar acento, tipografía y alternar a veces `split`/`blur`/subs de grupo.

## Gancho (investigación 2026-11-18, shared/investigaciones/investigacion-2026-11-18-mejoras-clips.md)
- El fotograma 1 es lo más intenso (choque, cara de reacción). Si el clímax llega después de 5 s → `cold-open` (1-2 s del clímax y luego desde el principio).
- Titular = riesgo / superlativo / hueco de curiosidad ("He almost lost it all…", "Nobody expected GTA 6 to let you do this…"), nunca solo describir.
- Cuanto más corto mejor (20-35 s): la retención se mide sobre el total.

## Estructura (20-40 s; máx. 59)
1. **0-1 s gancho**: la imagen ya es el momento (o cold-open con el clímax) + texto de ≤7 palabras.
2. Planteamiento mínimo (qué intenta hacer) → **reacción**. Cortar en la reacción, nunca volver al chat.
3. Cambio visual cada 1-2 s (gameplay, subs palabra a palabra, replay/etiqueta si ayuda). Cámara fija / just chatting → layout `zoom` + `"punch": true`.
   Layouts: gameplay con facecam → `split`; persona hablando a cámara → `zoom` (+punch); mixto → `blur`.
4. Últimos ~2,5 s: pregunta para comentarios. Final que enlace con el principio (bucle).
5. **Aporte propio** obligatorio: contexto escrito por nosotros (gancho + `aporte` + descripción), recorte exacto, subtítulos limpios, reencuadre.

## Variedad (bloqueante, variedad_check.py)
Rotar tipo de gancho, estructura, color de acento, tipografía, layout y streamer. Nunca dos ganchos/preguntas parecidos en 15 Shorts.

## Subtítulos
Idioma del clip. Quitar los diálogos que el juego ya subtitula en pantalla. Nombres propios corregidos. Tacos con asteriscos.

## SEO
- Título: streamer + situación + una palabra en MAYÚSCULAS + 1-2 emojis, <70 car. Ej.: "Speed Watching His Own Stream TURNED Into A DISASTER 😭💀", "Kai Cenat got ROBBED by an NPC in GTA 6 😭". Nunca listas de streamers que no salen (spam).
- Descripción: 1.ª línea crédito (`🎥 Clip: twitch.tv/x`), 1-2 frases de contexto, pregunta. Hashtags: #GTA6 #<Streamer> #shorts.
- Tags: gta 6, gta vi, <streamer>, <streamer> gta 6, momento.

## Publicación
~5/día en HUECOS_UTC (13:00 16:00 18:00 20:00 22:30), ≥90 min de separación; `--ya` para momentos en caliente. Siempre privado programado + verificado.

## Pasos (un Short)
01 descargar_clip → 02 seleccion.json + recortar → 03 transcribir + corregir → 04 montar → 05 seo.json → 06 qa → preparar_meta → (si "súbelo tú") subir_shorts.
