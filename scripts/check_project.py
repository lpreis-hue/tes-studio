"""Fast structural checks that do not import GUI or solver packages."""

from __future__ import annotations

import hashlib
import json
import py_compile
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def fail(message: str) -> None:
    print(f"ERRO: {message}", file=sys.stderr)
    raise SystemExit(1)


required_files = (
    "main.py",
    "ico.ico",
    "thermodynamic_data.xlsx",
    "app/files/TeS.pdf",
    "app/files/msg.txt",
    "app/imgs/initial_v3.png",
    "app/imgs/minG.png",
    "app/imgs/maxS.png",
    "tes.spec",
    ".github/workflows/build-windows.yml",
)
for relative_path in required_files:
    if not (ROOT / relative_path).is_file():
        fail(f"arquivo obrigatório ausente: {relative_path}")

for path in ROOT.rglob("*.py"):
    if any(part in {"build", "dist", ".venv"} for part in path.parts):
        continue
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError as exc:
        fail(str(exc))

try:
    compile((ROOT / "tes.spec").read_text(encoding="utf-8"), "tes.spec", "exec")
except SyntaxError as exc:
    fail(f"tes.spec inválido: {exc}")

from app.find_path import resource_path

if Path(resource_path("ico.ico")) != ROOT / "ico.ico":
    fail("resolução de recursos depende do diretório atual")

manifest_path = ROOT / "numerical_core.sha256.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
for relative_path, expected_hash in manifest.items():
    actual_hash = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
    if actual_hash != expected_hash:
        fail(f"núcleo numérico alterado sem atualizar o manifesto: {relative_path}")

print("Estrutura, sintaxe e núcleo numérico verificados.")
