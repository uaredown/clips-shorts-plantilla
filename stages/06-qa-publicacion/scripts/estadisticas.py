"""Informe de estadísticas del canal con la YouTube Analytics API (copiado de Bow Tie Mind 2026-11-17, adaptado a Shorts).
Uso: python estadisticas.py [--dias 7]
     python estadisticas.py --paises <videoId> [--dias 28]   → % de vistas por país y % Tier 1 (prueba para campañas)
Saca: totales, tabla por Short (vistas, vistas comprometidas, duración media, % visto, retención a los 3 s = nota del gancho,
suscriptores) y fuentes de tráfico. Guarda en ../output/_estadisticas/<fecha>.md y lo resume en shared/metricas-canal.md a mano.
Notas: Analytics llega con 2-3 días de retraso (termina hace 3 días). "Visto vs. deslizado", impresiones y CTR NO están en
la API: se miran en Studio (Shorts > Visto vs. deslizado).
"""
import sys
from datetime import date, timedelta
from pathlib import Path

from googleapiclient.discovery import build

sys.path.insert(0, str(Path(__file__).parent))
import youtube_api as Y  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "output" / "_estadisticas"
FUENTES = {"SUBSCRIBER": "Exploración", "RELATED_VIDEO": "Sugeridos", "YT_SEARCH": "Búsqueda", "SHORTS": "Feed de Shorts",
           "NO_LINK_OTHER": "Directo/desconocido", "YT_OTHER_PAGE": "Otras páginas YT", "YT_CHANNEL": "Página del canal",
           "PLAYLIST": "Playlists", "EXT_URL": "Externo", "NOTIFICATION": "Notificaciones", "HASHTAGS": "Hashtags"}


def segundos(iso):
    import re
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    return sum(int(x or 0) * k for x, k in zip(m.groups(), (3600, 60, 1))) if m else 0


def retencion(q, vid, dur_iso, seg=3):
    """% de espectadores que siguen en el segundo `seg` (curva audienceWatchRatio)."""
    dur = segundos(dur_iso)
    if not dur:
        return "-"
    filas = (q("audienceWatchRatio", dimensions="elapsedVideoTimeRatio", filters=f"video=={vid}").get("rows") or [])
    if not filas:
        return "-"
    return f"{100 * min(filas, key=lambda f: abs(f[0] - seg / dur))[1]:.0f} %"


TIER1 = {"US", "GB", "CA", "AU", "NZ"}  # Reach: US/CA/AU/UK/NZ ≥50 %; Tomo (Clipping Nation): US/UK/CA/AU ≥40 %


def paises(vid, dias):
    a = build("youtubeAnalytics", "v2", credentials=Y.credenciales())
    fin, ini = date.today(), date.today() - timedelta(days=dias)
    r = a.reports().query(ids="channel==MINE", startDate=str(ini), endDate=str(fin), metrics="views",
                          dimensions="country", filters=f"video=={vid}", sort="-views").execute()
    filas = r.get("rows") or []
    tot = sum(f[1] for f in filas) or 1
    print(" · ".join(f"{p} {100 * v / tot:.0f} %" for p, v in filas[:8]) or "sin datos todavía (Analytics va con 2-3 días de retraso)")
    t1 = sum(v for p, v in filas if p in TIER1)
    t4 = sum(v for p, v in filas if p in TIER1 - {"NZ"})
    print(f"Tier 1 (US/UK/CA/AU/NZ): {100 * t1 / tot:.0f} %  ·  US/UK/CA/AU: {100 * t4 / tot:.0f} %  ·  {tot} vistas con país")


def main():
    if "--paises" in sys.argv:
        dias = int(sys.argv[sys.argv.index("--dias") + 1]) if "--dias" in sys.argv else 28
        return paises(sys.argv[sys.argv.index("--paises") + 1], dias)
    dias = int(sys.argv[sys.argv.index("--dias") + 1]) if "--dias" in sys.argv else 7
    fin = date.today() - timedelta(days=3)
    ini = fin - timedelta(days=dias - 1)
    a = build("youtubeAnalytics", "v2", credentials=Y.credenciales())

    def q(metrics, **k):
        try:
            return a.reports().query(ids="channel==MINE", startDate=str(ini), endDate=str(fin), metrics=metrics, **k).execute()
        except Exception as e:  # noqa: BLE001
            return {"error": str(e)[:200]}

    md = [f"# Estadísticas del canal ({ini} → {fin}, {dias} días)\n"]
    tot = q("views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,subscribersLost")
    if tot.get("rows"):
        v, m, avd, pct, sg, sl = tot["rows"][0]
        md.append(f"**Totales:** {v:,} vistas · {m / 60:,.1f} h · duración media {avd} s · {pct:.1f} % visto · "
                  f"+{sg - sl} suscriptores\n")
    vid = q("views,engagedViews,averageViewDuration,averageViewPercentage,subscribersGained",
            dimensions="video", sort="-views", maxResults=50)
    if "error" in vid:  # engagedViews no disponible → sin ella
        vid = q("views,views,averageViewDuration,averageViewPercentage,subscribersGained",
                dimensions="video", sort="-views", maxResults=50)
    ids = [r[0] for r in vid.get("rows", [])]
    info = {}
    yt = Y.yt()
    for k in range(0, len(ids), 50):
        for it in yt.videos().list(part="snippet,contentDetails", id=",".join(ids[k:k + 50])).execute()["items"]:
            info[it["id"]] = (it["snippet"]["title"], it["contentDetails"]["duration"])
    md += ["| Short | Vistas | Comprom. | Dur. media | % visto | Ret. 3 s | Subs |", "|---|---|---|---|---|---|---|"]
    for r in vid.get("rows", []):
        t, dur = info.get(r[0], (r[0], ""))
        md.append(f"| [{t[:55]}](https://youtu.be/{r[0]}) | {r[1]} | {r[2]} | {r[3]} s | {r[4]:.0f} % | "
                  f"{retencion(q, r[0], dur) if r[1] >= 30 else '-'} | {r[5]} |")
    traf = q("views", dimensions="insightTrafficSourceType", sort="-views")
    if traf.get("rows"):
        tt = sum(r[1] for r in traf["rows"]) or 1
        md.append("\n**Fuentes:** " + " · ".join(f"{FUENTES.get(r[0], r[0])} {100 * r[1] / tt:.1f} %" for r in traf["rows"]))
    OUT.mkdir(parents=True, exist_ok=True)
    salida = OUT / f"{fin}.md"
    salida.write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md[:3]))
    print(f"({len(ids)} Shorts) -> {salida}")


if __name__ == "__main__":
    main()
