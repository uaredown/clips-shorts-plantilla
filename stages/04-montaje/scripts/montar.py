"""Monta el Short vertical 1080×1920 (≤59 s): layout + gancho + subtítulos palabra a palabra quemados + crédito + pregunta final.
Uso: python montar.py <short-NNN-slug>
Entradas: 02/<slug>/seleccion.json + clip.mp4 · 03/<slug>/palabras.json
Salidas en stages/04-montaje/output/<slug>/: final.mp4, final.srt (para subir a YouTube), subs.ass, montaje.json
Antes de renderizar pasa variedad_check.py (si falla, NO exporta). Solo los seleccion.json con "prueba": true se lo saltan.

Campos de seleccion.json que usa: layout (split|zoom|blur), facecam [x,y,w,h] (fracciones, para split), centro_x/zoom (zoom),
acento "#RRGGBB", fuente, pos_subs (centro|bajo), gancho, gancho_dur (s, def. 2.0), pregunta, canal_url,
segmentos [{desde, hasta, vel, etiqueta}] en segundos de clip.mp4 (def.: el clip entero).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
import emojis  # noqa: E402
import variedad_check  # noqa: E402

RAIZ = Path(__file__).resolve().parents[3]
SFX = RAIZ / "shared" / "sfx"
W, H = 1080, 1920


def ass_color(hexrgb, alpha="00"):
    h = hexrgb.lstrip("#")
    return f"&H{alpha}{h[4:6]}{h[2:4]}{h[0:2]}".upper()


def ts(t):
    t = max(t, 0)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def srt_ts(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def limpio(txt):
    return txt.replace("{", "(").replace("}", ")").replace("\\", "")


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-show_entries", "format=duration", "-of", "json", str(path)], capture_output=True, text=True)
    j = json.loads(r.stdout)
    return j["streams"][0]["width"], j["streams"][0]["height"], float(j["format"]["duration"])


def remapear(palabras, segs):
    """Pasa los tiempos de clip.mp4 al tiempo final (segmentos concatenados con su velocidad)."""
    out, off = [], 0.0
    for g in segs:
        a, b, v = g["desde"], g["hasta"], g.get("vel", 1)
        for p in palabras:
            if a <= p["s"] < b:
                out.append({"w": p["w"], "s": off + (p["s"] - a) / v, "e": off + (min(p["e"], b) - a) / v})
        g["_ini"], g["_fin"] = off, off + (b - a) / v
        off = g["_fin"]
    return out, off


def grupos(pal, maxw=3, maxc=18):
    gs, cur = [], []
    for i, p in enumerate(pal):
        if cur and (len(cur) >= maxw or p["s"] - cur[-1]["e"] > 0.5
                    or len(" ".join(x["w"] for x in cur + [p])) > maxc or re.search(r"[.?!¿¡]$", cur[-1]["w"])):
            gs.append(cur)
            cur = []
        cur.append(p)
    if cur:
        gs.append(cur)
    return gs


def layout_filtro(s, sw, sh):
    lay = s["layout"]
    if lay == "zoom" or sw / sh < 0.6:  # fuente ya vertical: rellenar
        z, cx = s.get("zoom", 1.0), s.get("centro_x", 0.5)
        return (f"[vc]crop=w='min(iw,ih*9/16)/{z}':h='ih/{z}':x='(iw-ow)*{cx}':y='(ih-oh)/2',"
                f"scale={W}:{H},setsar=1[lay]")
    if lay == "blur":
        fg = "[b2]"
        if s.get("juego"):  # primer plano = solo la zona del juego (sin chat ni contadores), más grande
            gx, gy, gw, gh = s["juego"]
            fg = f"[b2]crop=iw*{gw}:ih*{gh}:iw*{gx}:ih*{gy},"
        return (f"[vc]split[b1][b2];[b1]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"boxblur=25:3,eq=brightness=-0.12[bg];{fg}scale={W}:-2[fg];"
                f"[bg][fg]overlay=0:(H-h)/2,setsar=1[lay]")
    if lay == "split":
        fx, fy, fw, fh = s["facecam"]
        if s.get("juego"):  # zona exacta del juego (sin facecam superpuesta ni chat)
            gx, gy, gw, gh = s["juego"]
            return (f"[vc]split[g][f];[g]crop=iw*{gw}:ih*{gh}:iw*{gx}:ih*{gy},scale={W}:1100:force_original_aspect_ratio=increase,"
                    f"crop={W}:1100[gt];[f]crop=iw*{fw}:ih*{fh}:iw*{fx}:ih*{fy},scale={W}:820:force_original_aspect_ratio=increase,"
                    f"crop={W}:820[fb];[gt][fb]vstack,setsar=1[lay]")
        return (f"[vc]split[g][f];[g]crop=ih*{W}/1100:ih:(iw-ow)/2:0,scale={W}:1100[gt];"
                f"[f]crop=iw*{fw}:ih*{fh}:iw*{fx}:ih*{fy},scale={W}:820:force_original_aspect_ratio=increase,"
                f"crop={W}:820[fb];[gt][fb]vstack,setsar=1[lay]")
    if lay == "stack":  # estilo de los clips virales: cara ARRIBA grande, juego ABAJO (investigación 2026-11-18)
        fx, fy, fw, fh = s["facecam"]
        if s.get("juego"):  # zona exacta del juego [x,y,w,h] (sin la facecam superpuesta ni el chat)
            gx, gy, gw, gh = s["juego"]
            g = (f"[g]crop=iw*{gw}:ih*{gh}:iw*{gx}:ih*{gy},scale={W}:960:force_original_aspect_ratio=increase,"
                 f"crop={W}:960[gb]")
        else:
            g = f"[g]crop=ih*{W}/960:ih:(iw-ow)*{s.get('centro_x', 0.5)}:0,scale={W}:960[gb]"
        return (f"[vc]split[g][f];[f]crop=iw*{fw}:ih*{fh}:iw*{fx}:ih*{fy},scale={W}:960:force_original_aspect_ratio=increase,"
                f"crop={W}:960[ft];{g};[ft][gb]vstack,setsar=1[lay]")
    sys.exit(f"layout desconocido: {lay}")


def main():
    slug = sys.argv[1]
    d02 = RAIZ / "stages/02-seleccion-gancho/output" / slug
    s = json.loads((d02 / "seleccion.json").read_text(encoding="utf-8"))
    if not s.get("prueba"):
        err = variedad_check.check(slug)
        if err:
            sys.exit("VARIEDAD FALLA (no se exporta):\n- " + "\n- ".join(err))
    out = RAIZ / "stages/04-montaje/output" / slug
    out.mkdir(parents=True, exist_ok=True)
    clip = d02 / "clip.mp4"
    sw, sh, cdur = probe(clip)
    segs = s.get("segmentos") or [{"desde": 0, "hasta": cdur, "vel": 1}]
    pj = json.loads((RAIZ / "stages/03-transcripcion-subs/output" / slug / "palabras.json").read_text(encoding="utf-8"))
    pal, total = remapear(pj["palabras"], segs)
    if total > 59.05:
        sys.exit(f"BLOQUEADO: {total:.1f}s > 59 s")

    acento, fuente = s["acento"], s["fuente"]
    sub_y = {"split": {"centro": 1100, "bajo": 1700}, "stack": {"centro": 960, "bajo": 1500}}.get(
        s["layout"], {"centro": 1200, "bajo": 1480})[s["pos_subs"]]
    palabra = s.get("subs_estilo") == "palabra"   # una palabra gigante cada vez (estilo de los clips virales)
    ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "",
           "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
           "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
           "MarginR, MarginV, Encoding",
           f"Style: Sub,{fuente},92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,8,4,5,60,60,0,1",
           f"Style: Hook,{fuente},96,&H00000000,&H00000000,{ass_color(acento)},&H00000000,-1,0,0,0,100,100,1,0,3,20,0,8,80,80,0,1",
           "Style: Credit,Bahnschrift,40,&H30FFFFFF,&H30FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,1,0,1,3,0,8,40,40,0,1",
           f"Style: Preg,{fuente},70,&H00FFFFFF,&H00FFFFFF,&H50000000,&H00000000,-1,0,0,0,100,100,1,0,3,22,0,5,90,90,0,1",
           f"Style: Big,{fuente},132,{ass_color(acento)},&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,1,0,1,11,0,5,40,40,0,1",
           f"Style: Titular,{fuente},62,&H00FFFFFF,&H00FFFFFF,&H40000000,&H00000000,-1,0,0,0,100,100,0,0,3,18,0,8,70,70,0,1",
           f"Style: Etiq,{fuente},64,{ass_color(acento)},&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,2,0,1,6,0,8,40,40,0,1",
           "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    ev = lambda l, a, b, st, t: ass.append(f"Dialogue: {l},{ts(a)},{ts(b)},{st},,0,0,0,,{t}")  # noqa: E731
    credito = re.sub(r"^https?://(www\.)?", "", s["canal_url"]).rstrip("/")
    ev(0, 0, total, "Credit", f"{{\\pos(540,36)}}{limpio(credito)}")
    if s.get("titular"):  # titular fijo todo el vídeo: imagen con emojis a color (emojis.py), se superpone al final
        emojis.titular_png(s["titular"], fuente, out / "titular.png")
    gd = 0 if s.get("titular") else s.get("gancho_dur", 2.0)
    ev(3, 0, gd, "Hook", "{\\pos(540,190)\\fscx70\\fscy70\\t(0,120,\\fscx100\\fscy100)}" + limpio(s["gancho"]).upper())
    for g in segs:
        if g.get("etiqueta"):
            ev(3, g["_ini"], g["_fin"], "Etiq", f"{{\\pos(540,110)}}{limpio(g['etiqueta']).upper()}")
    hl = ass_color(acento)
    gs = grupos(pal, maxw=1 if palabra else 3)
    for k, grp in enumerate(gs):
        fin_grp = min(grp[-1]["e"] + 0.3, gs[k + 1][0]["s"] if k + 1 < len(gs) else total)
        for i, p in enumerate(grp):
            a = p["s"]
            b = grp[i + 1]["s"] if i + 1 < len(grp) else fin_grp
            txt = " ".join((f"{{\\c{hl}&}}{limpio(x['w']).upper()}{{\\c&H00FFFFFF&}}" if j == i else limpio(x["w"]).upper())
                           for j, x in enumerate(grp))
            pop = "\\fscx108\\fscy108\\t(0,90,\\fscx100\\fscy100)" if i == 0 else ""
            if palabra:
                ev(1, a, max(b, a + 0.05), "Big", f"{{\\pos(540,{sub_y})\\fscx118\\fscy118\\t(0,80,\\fscx100\\fscy100)}}"
                   + limpio(p["w"]).upper().strip(".,!?"))
            else:
                ev(1, a, max(b, a + 0.05), "Sub", f"{{\\pos(540,{sub_y}){pop}}}{txt}")
    pd = min(2.8, total / 4)
    if s.get("pregunta_en_pantalla", True):
        ev(4, total - pd, total, "Preg", "{\\pos(540,560)\\fad(150,0)}" + limpio(s["pregunta"]))
    if s.get("cta"):  # llamada a la acción que exigen algunas campañas (p. ej. Tomo): últimos segundos, bajo la pregunta
        ev(4, total - max(pd, 3.5), total, "Hook", "{\\pos(540,700)\\fad(150,0)}" + limpio(s["cta"]))
    (out / "subs.ass").write_text("\n".join(ass) + "\n", encoding="utf-8-sig")

    # SRT para subir (frases de ~7 palabras, tiempos finales)
    srt, n, i = [], 1, 0
    while i < len(pal):
        frase = pal[i:i + 7]
        srt += [str(n), f"{srt_ts(frase[0]['s'])} --> {srt_ts(frase[-1]['e'])}", " ".join(p["w"] for p in frase), ""]
        n, i = n + 1, i + 7
    (out / "final.srt").write_text("\n".join(srt), encoding="utf-8")

    # "punch": true (solo layout zoom) → trozos de ~punch_s s alternando zoom normal / zoom x1.18 (cambio visual cada 2-3 s)
    punch = s.get("punch") and (s["layout"] == "zoom" or sw / sh < 0.6)
    trozos = []
    for g in segs:
        v, a = g.get("vel", 1), g["desde"]
        paso = s.get("punch_s", 2.5) * v if punch else g["hasta"] - g["desde"]
        while a < g["hasta"] - 0.05:
            b = min(a + paso, g["hasta"])
            if g["hasta"] - b < 0.8 * v:  # no dejar un trozo final diminuto
                b = g["hasta"]
            trozos.append({"desde": a, "hasta": b, "vel": v})
            a = b
    z0, cx = s.get("zoom", 1.0), s.get("centro_x", 0.5)
    fc = []
    for k, g in enumerate(trozos):
        v = g["vel"]
        cadena = f"[0:v]trim=start={g['desde']}:end={g['hasta']},setpts=(PTS-STARTPTS)/{v}"
        if punch:
            z = z0 * (1.18 if k % 2 else 1.0)
            cadena += (f",crop=w='min(iw,ih*9/16)/{z}':h='ih/{z}':x='(iw-ow)*{cx}':y='(ih-oh)/2',"
                       f"scale={W}:{H},setsar=1")
        fc.append(cadena + f"[v{k}]")
        fc.append(f"[0:a]atrim=start={g['desde']}:end={g['hasta']},asetpts=PTS-STARTPTS,atempo={v}[a{k}]")
    fc.append("".join(f"[v{k}][a{k}]" for k in range(len(trozos))) + f"concat=n={len(trozos)}:v=1:a=1[vc0][ac]")
    fc.append("[vc0]fps=30[vc]")
    lay = "[vc]null[lay]" if punch else layout_filtro(s, sw, sh)
    # calidad (2026-11-19, "la calidad es un poco mala"): escalado lanczos (-sws_flags) + enfoque suave tras ampliar recortes
    fc.append(lay[:-len("[lay]")] + "[lay0]")
    fc.append("[lay0]unsharp=5:5:0.6:5:5:0.0[lay]")

    # --- efectos en momentos clave: seleccion.json "efectos": [{"t": s_final, "tipo": "boom|whoosh|pop|ding|riser",
    #     "zoom": true, "shake": true, "flash": true, "emoji": "😭"}] + whoosh automático en cada corte entre segmentos
    efectos = list(s.get("efectos", []))
    if s.get("whoosh_cortes", True):
        efectos += [{"t": max(g["_ini"] - 0.15, 0), "tipo": "whoosh", "vol": 0.5} for g in segs[1:]]
    entradas, vl = [], "lay"

    def nueva_entrada(*args):
        entradas.extend(args)
        return 1 + sum(1 for x in entradas if x == "-i") - 1
    if s.get("inicio_punch", True):  # zoom de golpe en el primer fotograma (rompe el patrón antes del deslizar)
        efectos.append({"t": 0.0, "zoom": True})
    zs = [e for e in efectos if e.get("zoom")]
    zl = s.get("zoom_lento")  # [a, b] en tiempo final: acercamiento lento (x1.12) durante una reacción
    if zs or zl:
        z = "+".join([f"0.16*between(it,{e['t']:.2f},{e['t'] + 0.5:.2f})*(1-(it-{e['t']:.2f})/0.5)" for e in zs]
                     + ([f"0.12*between(it,{zl[0]},{zl[1]})*(it-{zl[0]})/({zl[1]}-{zl[0]})"] if zl else []))
        sk = "+".join(f"12*between(it,{e['t']:.2f},{e['t'] + 0.4:.2f})*sin(it*95)" for e in zs if e.get("shake"))
        x = "iw/2-(iw/zoom/2)" + (f"+({sk})" if sk else "")
        fc.append(f"[{vl}]zoompan=z='1+{z}':x='{x}':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps=30[zp]")
        vl = "zp"
    fl = [e for e in efectos if e.get("flash")]
    if fl:
        en = "+".join(f"between(t,{e['t']:.2f},{e['t'] + 0.08:.2f})" for e in fl)
        fc.append(f"[{vl}]eq=brightness=0.35:enable='{en}'[fl]")
        vl = "fl"
    fc.append(f"[{vl}]ass=subs.ass[va]")
    vl = "va"
    if s.get("titular"):
        k = nueva_entrada("-i", "titular.png")
        fc.append(f"[{vl}][{k}:v]overlay=(W-w)/2:78[vt]")
        vl = "vt"
    for n, e in enumerate(e for e in efectos if e.get("emoji")):
        png = emojis.emoji_png(e["emoji"])
        if not png:
            continue
        png.resize((200, 200), Image.LANCZOS).save(out / f"emoji_{n}.png")
        k = nueva_entrada("-i", f"emoji_{n}.png")
        fc.append(f"[{k}:v]format=rgba[em{n}];[{vl}][em{n}]overlay=(W-w)/2:{sub_y - 300}:"
                  f"enable='between(t,{e['t']:.2f},{e['t'] + 0.9:.2f})'[ve{n}]")
        vl = f"ve{n}"
    fc.append(f"[{vl}]null[vo]")
    al = []
    for n, e in enumerate(e for e in efectos if e.get("tipo")):
        wav = SFX / f"{e['tipo']}.wav"
        if not wav.exists():
            continue
        k = nueva_entrada("-i", str(wav))
        ms = int(e["t"] * 1000)
        fc.append(f"[{k}:a]adelay={ms}|{ms},volume={e.get('vol', 0.8)}[sf{n}]")
        al.append(f"[sf{n}]")
    if al:
        fc.append(f"[ac]{''.join(al)}amix=inputs={len(al) + 1}:normalize=0:duration=first[am]")
    fc.append(f"[{'am' if al else 'ac'}]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[ao]")
    cmd = ["ffmpeg", "-v", "error", "-y", "-sws_flags", "lanczos+accurate_rnd+full_chroma_int", "-i", str(clip), *entradas, "-filter_complex", ";".join(fc), "-map", "[vo]", "-map", "[ao]",
           "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", "30",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "final.mp4"]
    r = subprocess.run(cmd, cwd=out, capture_output=True, text=True)
    if r.returncode:
        sys.exit("ffmpeg falló:\n" + r.stderr[-600:])
    fw, fh, fdur = probe(out / "final.mp4")
    (out / "montaje.json").write_text(json.dumps({"duracion": round(fdur, 2), "w": fw, "h": fh, "layout": s["layout"],
                                                  "idioma": pj["idioma"], "palabras": len(pal)}, indent=1), encoding="utf-8")
    print(f"ok final.mp4 {fw}x{fh} · {fdur:.1f}s · {s['layout']} · {len(gs)} grupos de subs · idioma {pj['idioma']}")


if __name__ == "__main__":
    main()
