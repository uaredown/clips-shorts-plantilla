# 05 · SEO

**Cargar:** `shared/receta-produccion.md` (sección SEO) · `../02-seleccion-gancho/output/<slug>/seleccion.json`.
**Hacer:** escribir `output/<slug>/seo.json` en el idioma del clip:
```json
{"titulo": "Streamer + momento concreto + emoción (<70 car.)",
 "descripcion": "🎥 Clip: twitch.tv/<streamer>  ← 1.ª línea SIEMPRE el crédito\n1-2 frases con el contexto propio\n\npregunta",
 "tags": ["gta 6", "<streamer>", "<streamer> gta 6", "gta vi", "..."],
 "hashtags": ["#GTA6", "#<Streamer>", "#shorts"], "idioma": "en (opcional; si falta, el detectado)", "sintetico": false}
```
- **CORE:** título/texto en inglés que nombre a CORE o a los miembros; hashtags `#CORE` + uno por miembro que sale (#Lacy #Silky #JasonTheWeen #Adapt #Marlon #StableRonaldo); nada negativo sobre ellos. qa.py lo comprueba.
- Sin "leak", "filtrado", "spoiler" ni marcas en mayúsculas engañosas. Lo que promete el título tiene que salir en el clip.
- Sin miniatura (en Shorts casi no se ve y ahorra cuota); si un día se quiere, `miniatura` en meta.json.
**Producir:** `output/<slug>/seo.json`.
