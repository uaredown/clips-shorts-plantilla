# 06 · QA y publicación

**Cargar:** `output/<slug>/qa.json` + `hoja.jpg` (una imagen). Nada más.
**Hacer (scripts/ desde esta carpeta):**
1. `python qa.py <slug>` → duración, resolución, audio, srt, permiso ok, variedad, sin prueba/spoiler, crédito en la 1.ª línea. Mirar `hoja.jpg`.
2. `python preparar_meta.py <slug> [--srt]` → `output/<slug>/meta.json` (exige QA ok). Sin `--srt` por cuota: 5 × 1.600 = 8.000/10.000 (subs ya quemados). Con srt+playlist serían 10.250 → no caben 5.
3. **Solo si el usuario ha dicho "súbelo tú"**: `python subir_shorts.py plan` → `python subir_shorts.py subir 1 [--ya]` (privado programado, verifica privado + publishAt, apunta youtu.be en `shared/registros/registro-AAAA-Wss.md`, borra fuente.mp4/clip.mp4). Si no, dejar meta.json listo y preguntar.
**API (credenciales/ propias, puerto 8082):** `python youtube_api.py auth|canal|prueba|verificar <id> [publishAt]`.
- Token caduca ~7 días (invalid_grant): lanzar `auth` en segundo plano y avisar al usuario para que inicie sesión y elija el tu canal.
- Playlist: la inserción tarda ~1 min en verse → NO repetir (se duplica).
- CTR, impresiones y "visto vs. deslizado" no salen por la API: Studio. Analytics llega con 2-3 días de retraso.
- 403 en miniatura → verificar canal en youtube.com/verify (pedírselo al usuario).
- Proyecto de Cloud sin auditar → vídeos "Privado (bloqueado)": comprobar el primer Short real a su hora (ver shared/decisiones.md).
- **Campañas (CORE):** el usuario tiene que enviar el enlace en Content Rewards en los **30 min** siguientes a la hora de publicación → avisarle con la lista de horas y enlaces tras programar.
- **Tomo:** al pasar 2.000 vistas, `python estadisticas.py --paises <id>` y darle al usuario el % de países para la captura en Discord. Nunca borrar un Short de campaña antes de 30 días.
**Medir (cada lunes):** `python estadisticas.py --dias 7` → resumir en `shared/metricas-canal.md` y anotar vistas/% visto en el registro.
