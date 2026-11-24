# 03 · Transcripción y subtítulos

**Cargar:** solo `output/<slug>/texto.txt` tras transcribir.
**Hacer:** `python scripts/transcribir.py <slug> [--modelo medium] [--idioma es]` (faster-whisper local, gratis; `small` por defecto, `medium` si el audio es sucio o el idioma no es inglés).
- Leer `texto.txt` y corregir en `palabras.json` nombres propios y errores obvios (no tocar tiempos salvo error claro).
- Si el juego ya subtitula un diálogo (sale en pantalla), quitar esas palabras de `palabras.json`: se duplican con los nuestros.
- Insultos fuertes: dejarlos en audio, pero en el subtítulo usar asteriscos (f*ck) para no perder anunciantes.
**Producir:** `output/<slug>/palabras.json` ({idioma, palabras:[{w,s,e}]}) + `texto.txt`. El idioma detectado manda en metadatos y subtítulos.
