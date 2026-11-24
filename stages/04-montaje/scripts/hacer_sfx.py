"""Genera los efectos de sonido del canal con ffmpeg (síntesis propia: sin copyright ni Content ID).
Uso: python hacer_sfx.py  → shared/sfx/{boom,whoosh,pop,ding,riser}.wav (48 kHz)
- boom: golpe grave con caída (momento clave) · whoosh: barrido de ruido (cortes) · pop: clic corto (texto/emoji)
- ding: campanita (dato/acierto) · riser: subida de tensión de 1,2 s (antes del clímax)
"""
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parents[3] / "shared" / "sfx"
SFX = {
    "boom": ["-f", "lavfi", "-i", "aevalsrc=exprs='0.95*sin(2*PI*(62-30*t)*t)*exp(-3.5*t)+0.25*sin(2*PI*31*t)*exp(-2*t)':d=1.0:s=48000"],
    "whoosh": ["-f", "lavfi", "-i", "anoisesrc=d=0.5:c=pink:a=0.9:r=48000",
               "-af", "bandpass=f=1800:w=2400,afade=t=in:d=0.22,afade=t=out:st=0.24:d=0.26,volume=1.6"],
    "pop": ["-f", "lavfi", "-i", "aevalsrc=exprs='0.8*sin(2*PI*(1100-500*t)*t)*exp(-45*t)':d=0.14:s=48000"],
    "ding": ["-f", "lavfi", "-i", "aevalsrc=exprs='0.45*(sin(2*PI*1318*t)+0.5*sin(2*PI*2637*t)+0.25*sin(2*PI*3955*t))*exp(-4.5*t)':d=1.1:s=48000"],
    "riser": ["-f", "lavfi", "-i", "aevalsrc=exprs='0.35*sin(2*PI*(200+900*t*t)*t)*(t/1.2)':d=1.2:s=48000",
              "-af", "afade=t=out:st=1.1:d=0.1"],
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for n, args in SFX.items():
        subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-ac", "2", str(OUT / f"{n}.wav")], check=True)
    print("ok", ", ".join(f"{n}.wav" for n in SFX), "→", OUT)
