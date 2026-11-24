# <Nombre del canal> — Shorts de clips de streamers (orientación para Claude Code)

Canal de YouTube Shorts con los mejores momentos de streamers jugando a <juego>, en el idioma de cada clip, con subida automática por API. **Habla con el usuario en <idioma>.**

## Empezar aquí
- Short nuevo: leer **`shared/receta-produccion.md`** + el `CONTEXT.md` de la etapa. Nada más salvo que lo pida.
- Registro de lo subido: `shared/registros/registro-AAAA-Wss.md` (uno por semana).
- Lecciones del canal original: `docs/lecciones.md`.

## Cómo trabajar (ICM)
- La carpeta es la arquitectura: `stages/0N-nombre/` con su `CONTEXT.md`; el output de una etapa es el input de la siguiente. Sin orquestadores.
- Mismo slug en todas las etapas: `stages/0N/output/short-NNN-streamer-momento/`. Pruebas: `short-000-*` con `"prueba": true` u `output/_pruebas/<tema>/`.
- Lo que se repite 2 veces → script en `stages/0N/scripts/`. Scripts con salida corta.

## Etapas
01-fuentes-clips → 02-seleccion-gancho → 03-transcripcion-subs → 04-montaje → 05-seo → 06-qa-publicacion

## Reglas que no se saltan
Permiso del streamer `ok` · aporte propio · ≤59 s · sin spoilers de historia ni filtraciones · variedad_check · QA antes de subir · subir solo si el usuario lo ha autorizado · nada de pagar sin preguntar.
