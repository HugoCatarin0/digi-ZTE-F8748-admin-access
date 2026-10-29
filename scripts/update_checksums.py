#!/usr/bin/env python3
"""Atualiza hashes dos scripts, sem ler dados privados nem contactar o router."""
import hashlib
from pathlib import Path
root = Path(__file__).resolve().parent.parent
paths = sorted(p for p in (root/'scripts').iterdir() if p.is_file())
(root/'SHA256SUMS.txt').write_text(''.join(
    hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(root).as_posix()+'\n'
    for p in paths))
print('SHA256SUMS.txt atualizado; rever diff antes de publicar.')
