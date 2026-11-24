# Campañas de clipping (Content Rewards) — guía completa

Las campañas pagan por las vistas de tus Shorts de un streamer concreto. Al empezar son el único ingreso real: la monetización de YouTube tarda meses (ver `docs/lecciones.md`).

## 1. Darse de alta
1. Crea una cuenta en **contentrewards.com** (sección de creadores, `/c/`).
2. **Conecta tu canal de YouTube** en Settings → cuentas vinculadas. Solo cuentan los clips publicados desde cuentas vinculadas.
3. En **Campaigns → Discover** busca campañas del juego/streamers de tu canal (agencias habituales: Reach, Clipping Nation, Clipped & Shipped) y pulsa **Join**.
4. Lee las **reglas** de cada una (suelen enlazar a un Google Doc o Notion) y pásalas a:
   - `shared/campanas.md`: resumen humano + **URL de envío** de la campaña.
   - `shared/campanas.json`: lo que comprueba `qa.py` (hashtags, a quién mencionar, mínimo de miembros, idioma, fecha de fin).
   - `shared/permisos-streamers.md`: el streamer pasa a `ok` con la campaña como prueba.

## 2. Tipos de pago (fíjate antes de unirte)
| Tipo | Cómo paga | Qué mirar |
|---|---|---|
| **Pool** (bolsa) | Reparte una bolsa fija según vistas | Mínimo de vistas por clip (500-1.000) y vistas totales para cobrar (400k-750k) |
| **CPM** | X $ por cada 1.000 vistas | Pago mínimo por clip, máximo por clip y **presupuesto restante** (si se agota, la campaña se pausa) |

Reglas habituales: hashtag obligatorio (#Streamer), nombrar al streamer en título/descripción, el streamer como protagonista todo el vídeo, **sin logos** (ni mascota del canal), nada negativo sobre él, sin bots ni resubidas, a veces un % mínimo de público de países anglófonos.

## 3. Hacer el Short para una campaña
En `seleccion.json`: `"campanas": ["<Nombre>"]` y `"miembros": [...]`. En `seo.json`: el hashtag y el nombre exigidos. `qa.py` falla si falta algo.

## 4. Enviar el enlace (≤30 min tras publicarse)
Content Rewards rechaza el clip si han pasado más de 30 minutos desde que se publicó ("Posts have to be submitted within 30 minutes of going live").
1. Abre la URL de la campaña → **Submit clip**.
2. Pega el enlace `https://youtu.be/<id>` en "Paste a link".
3. Marca "I've read the requirements…" → **Submit clip** → debe salir **"Clip submitted"**.
4. Apúntalo: `python stages/06-qa-publicacion/scripts/marcar_envio.py <slug> "<campaña>"`.
5. Si sale "took too long", reintenta cada 3-5 min.

Los Shorts se suben como privados programados (`subir_shorts.py`), así que sabes la hora exacta de publicación: programa el envío para **la hora y 01**.

## 5. Automatizar los envíos con Claude Code
Con un MCP de navegador (p. ej. browser-mcp, que usa tu Chrome con la sesión de Content Rewards ya iniciada), Claude puede hacer el envío solo. Programa un recordatorio **de una sola vez** (CronCreate, no recurrente: los recurrentes llegan con retraso) a la hora de publicación + 1 min con este texto:

```
Envío URGENTE (ventana de 30 min desde las HH:00) del <slug> a la campaña <Nombre> (<URL de la campaña>).
1) cat stages/06-qa-publicacion/output/<slug>/subido.json (si no existe, avisar y parar);
2) navegador: abrir la URL en pestaña nueva y traerla al frente, click "Submit clip",
   rellenar input[placeholder="Paste a link"] con el youtu.be, captura para localizar la casilla
   de requisitos y el botón Submit, click en ambos, esperar "Clip submitted";
3) marcar_envio.py <slug> "<Nombre>" Claude; 4) cerrar la pestaña; responder en 1 línea.
```

Trampas:
- La pestaña tiene que estar **al frente** (Chrome no entrega clics a pestañas en segundo plano).
- El MCP del navegador se desconecta tras horas sin uso: programa un aviso horario que solo liste las pestañas para mantenerlo vivo.
- Los recordatorios de CronCreate **solo existen mientras la sesión de Claude Code esté abierta**. La subida a YouTube, en cambio, la hace una tarea de Windows (`subir_programado.bat`) y no depende de Claude.
- La posición de la casilla y del botón cambia con el tamaño de la ventana: localízalos siempre con una captura.

## 6. Seguimiento
- **Submissions** en Content Rewards: estado de cada envío (pendiente, aprobado, rechazado).
- Una campaña **pausada** (sin presupuesto) no acepta envíos, pero las vistas siguen contando por si la reactivan.
- Si un streamer o agencia pide retirar un clip: borrarlo ese día y pasar al streamer a `no`.
