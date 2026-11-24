# Permisos de streamers (fuente de verdad para 01-fuentes-clips)

Solo se clipea a quien tenga estado **ok**. `descargar_clip.py` lo comprueba y se niega si no.
Estados: `ok` (permiso comprobado, con prueba) · `riesgo` (SIN permiso, el usuario acepta el riesgo de strikes: se permite clipear) · `pendiente` (pedido / sin comprobar) · `no` (prohibido).
Prueba = enlace a su regla de clips, programa de clipping, o mensaje de permiso. Fecha de comprobación obligatoria.
Si un streamer pide retirar algo: se borra el Short ese día y pasa a `no`.
Detalle: `shared/investigaciones/ (cómo comprobar permisos)`.

| streamer | plataforma | idioma | estado | prueba (enlace) | comprobado |
|---|---|---|---|---|---|
| _prueba_ | - | - | ok | solo para output/_pruebas, nunca se publica | 2026-11-17 |
| EjemploStreamer | twitch | en | pendiente | enlace a su regla de clips o campaña de clipping | AAAA-MM-DD |

