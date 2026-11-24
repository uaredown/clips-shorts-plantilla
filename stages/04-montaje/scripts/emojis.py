"""Emojis a color estilo iPhone en los textos del vídeo (libass no pinta emojis a color).
- emoji_png(e): descarga una vez el PNG de 64 px (paquete npm emoji-datasource-apple, vía jsdelivr) a shared/emojis/ y lo devuelve.
- titular_png(texto, fuente, salida): dibuja el titular (caja negra redondeada, texto blanco, emojis a color, hasta 2 líneas).
Nota: el arte de los emojis es de Apple (uso muy extendido en vídeos). Si diera problemas, cambiar URL a Twemoji (CC-BY).
Uso de prueba: python emojis.py "Kai Cenat wasn't ready 😭💀"   → shared/emojis/_prueba_titular.png
"""
import re
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[3]
CACHE = RAIZ / "shared" / "emojis"
URL = "https://cdn.jsdelivr.net/npm/emoji-datasource-apple@16.0.0/img/apple/64/{}.png"
FUENTES = {"Impact": "impact.ttf", "Bahnschrift": "bahnschrift.ttf", "Segoe UI Black": "seguibl.ttf"}
EMOJI_RE = re.compile("(?:[\U0001F1E6-\U0001F1FF]{2})|(?:[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]"
                      "\uFE0F?(?:\u200D[\U0001F300-\U0001FAFF\u2600-\u27BF]\uFE0F?)*)")


def codigo(e, sin_fe0f=False):
    cps = [f"{ord(c):x}" for c in e if not (sin_fe0f and c == "\ufe0f")]
    return "-".join(cps)


def emoji_png(e):
    CACHE.mkdir(parents=True, exist_ok=True)
    for cod in (codigo(e), codigo(e, True)):
        f = CACHE / f"{cod}.png"
        if f.exists():
            return Image.open(f).convert("RGBA")
        try:
            with urllib.request.urlopen(URL.format(cod), timeout=20) as r:
                f.write_bytes(r.read())
            return Image.open(f).convert("RGBA")
        except Exception:  # noqa: BLE001  (probar sin FE0F)
            continue
    return None


def trozos(texto):
    """Divide el texto en [("t", palabra) | ("e", emoji)] respetando espacios."""
    out, pos = [], 0
    for m in EMOJI_RE.finditer(texto):
        if m.start() > pos:
            out.append(("t", texto[pos:m.start()]))
        out.append(("e", m.group()))
        pos = m.end()
    if pos < len(texto):
        out.append(("t", texto[pos:]))
    return out


def titular_png(texto, fuente, salida, tam=62, ancho_max=980, color_caja=(0, 0, 0, 175)):
    f = ImageFont.truetype("C:/Windows/Fonts/" + FUENTES.get(fuente, "impact.ttf"), tam)
    if fuente == "Bahnschrift":
        f.set_variation_by_name("Bold")
    em = int(tam * 1.05)
    # tokens (palabras y emojis) con su ancho
    toks = []
    for tipo, val in trozos(texto):
        if tipo == "e":
            toks.append(("e", val, em + 6))
        else:
            for w in re.split(r"(\s+)", val):
                if w:
                    toks.append(("t", w, f.getlength(w)))
    lineas, cur, ancho = [], [], 0
    for t in toks:
        if cur and ancho + t[2] > ancho_max - 60 and not t[1].isspace():
            lineas.append(cur)
            cur, ancho = [], 0
        if not cur and t[1].isspace():
            continue
        cur.append(t)
        ancho += t[2]
    if cur:
        lineas.append(cur)
    lineas = lineas[:2]
    alto_l = int(tam * 1.25)
    anchos = [sum(t[2] for t in l) for l in lineas]
    W, H = int(max(anchos) + 60), alto_l * len(lineas) + 34
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=26, fill=color_caja)
    y = 17
    for l, a in zip(lineas, anchos):
        x = (W - a) / 2
        for tipo, val, w in l:
            if tipo == "e":
                png = emoji_png(val)
                if png:
                    png = png.resize((em, em), Image.LANCZOS)
                    im.alpha_composite(png, (int(x + 3), int(y + (alto_l - em) / 2)))
            else:
                d.text((x, y + (alto_l - tam) / 2 - tam * 0.08), val, font=f, fill=(255, 255, 255, 255))
            x += w
        y += alto_l
    im.save(salida)
    return W, H


def sin_emojis(texto):
    return EMOJI_RE.sub("", texto).strip()


if __name__ == "__main__":
    s = CACHE / "_prueba_titular.png"
    CACHE.mkdir(parents=True, exist_ok=True)
    print(titular_png(sys.argv[1] if len(sys.argv) > 1 else "Kai Cenat wasn't ready 😭💀", "Impact", s), s)
