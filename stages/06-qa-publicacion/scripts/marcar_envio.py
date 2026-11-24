"""Apunta en el registro semanal que un Short se envió a una campaña de Content Rewards.
Uso: python marcar_envio.py <short-NNN-slug> "<campaña>" [quién: Claude|usuario]
"""
import sys
from pathlib import Path

REG = Path(__file__).resolve().parents[3] / "shared/registros"
slug, camp = sys.argv[1], sys.argv[2]
quien = sys.argv[3] if len(sys.argv) > 3 else "Claude"
for f in sorted(REG.glob("registro-*.md"), reverse=True):
    lineas = f.read_text(encoding="utf-8").splitlines()
    for i, l in enumerate(lineas):
        if l.startswith(f"| {slug} "):
            cols = l.split("|")
            cols[-2] = f" enviado a Content Rewards ({camp}) por {quien} "
            lineas[i] = "|".join(cols)
            f.write_text("\n".join(lineas) + "\n", encoding="utf-8")
            sys.exit(print(f"ok {f.name}: {slug} → {camp}"))
sys.exit(f"{slug} no está en ningún registro")
