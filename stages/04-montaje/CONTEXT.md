# 04 · Montaje vertical

**Cargar:** nada extra (montar.py lee 02 y 03).
**Hacer:** `python scripts/montar.py <slug>` → primero pasa `variedad_check.py` (si falla, cambiar seleccion.json en 02, no forzar).
- Revisar UNA hoja de contacto pequeña (la genera qa.py en 06, o `ffmpeg ... tile=4x1` a 270 px). Arreglos quirúrgicos: cambiar el campo de seleccion.json y volver a montar, no rehacer etapas.
**Producir:** `output/<slug>/final.mp4` (1080×1920, ≤59 s, -14 LUFS, subtítulos quemados, crédito arriba, gancho 0-2 s, pregunta final), `final.srt` (para subir), `subs.ass`, `montaje.json`.
**Un render cada vez.** Comprobar disco (`df -h /c`) si baja de 20 GB libres.
