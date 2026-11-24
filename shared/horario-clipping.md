# Horario de clipeo (desde 2026-11-18)

Petición del usuario: no parar; cada ~30 min sacar los momentos clave y virales de cada streamer en directo.

## Cada vuelta (cada 30 min)
1. `python stages/01-fuentes-clips/scripts/quien_en_directo.py` → quién emite (prioridad 1 = campaña que paga, 2 = Kai/Speed con riesgo).
2. Por cada streamer en directo, de más a menos prioridad:
   - **Twitch:** `buscar_clips.py <canal> --rango 24hr` → los clips que ha creado su propio chat en la última media hora son los momentos virales (la gente clipea lo que explota). Coger el más visto que aún no hayamos usado.
   - **YouTube en vivo (Speed, Tomo):** `descargar_clip.py ... --directo 180` y elegir con hoja de contacto + transcripción. Cuando acabe el directo: `momentos_youtube.py` (heatmap) o `escanear_vod.py`.
   - Comprobar: que sea el juego que toca (GTA 6), sin anuncio de Twitch, sin música, sin cinemática de historia ni final.
3. Producir el Short completo (02→06). Un render cada vez.
4. Programar en el siguiente hueco libre; si es un momento en caliente, `--ya`.
5. Apuntar en el registro semanal + darle al usuario hora y enlace para enviarlo a Content Rewards en 30 min (solo campañas).

## Límite real: la cuota de la API
- 10.000 unidades/día y cada subida cuesta 1.600 → **máximo 6 Shorts al día** (5 con margen).
- Clipear "a todos cada 30 min" produce muchos más: se quedan los mejores (prioridad campaña > vistas del clip original > frescura <24 h) y el resto se descarta.
- Para subir más hay que pedir más cuota a Google (formulario "YouTube API Services – Audit and Quota Extension"). Es gratis pero tarda días o semanas.

## Huecos por defecto
13:00 · 16:00 · 18:00 · 20:00 · 22:30 UTC (subir_shorts.py). Noche de calentamiento 2026-11-18: 02:15-06:15 UTC cada hora.

## Automatización (decisión 2026-11-18)
**Por tandas, no en continuo** (ahorro de tokens): en cada sesión se producen varios Shorts seguidos y se dejan programados con publishAt repartidos por los huecos. Las vueltas de 30 min de arriba son el procedimiento dentro de una tanda, no un bucle permanente.
