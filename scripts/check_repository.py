#!/usr/bin/env python3
"""Verifica o conteudo publicavel. Nao le dumps nem usa rede."""
import hashlib
from pathlib import Path
import re

root = Path(__file__).resolve().parent.parent
allowed_suffixes = {'.md', '.py', '.sh', '.txt', '.yml'}
files = [p for p in root.rglob('*') if p.is_file()
         and '.git' not in p.relative_to(root).parts
         and '__pycache__' not in p.relative_to(root).parts]
for path in files:
    rel = path.relative_to(root)
    if path.name != '.gitignore' and path.suffix not in allowed_suffixes:
        raise SystemExit('Ficheiro nao publicavel: ' + str(rel))
    data = path.read_text()
    if re.search(r'/(?:Users|home)/[^\s"\']+', data):
        raise SystemExit('Caminho pessoal em ' + str(rel))
    if path.suffix == '.md':
        for link in re.findall(r'\]\(([^)]+)\)', data):
            if '://' in link or link.startswith('#'):
                continue
            if not (path.parent / link.split('#')[0]).exists():
                raise SystemExit('Link local inexistente em ' + str(rel))
checks = root/'SHA256SUMS.txt'
if not checks.exists():
    raise SystemExit('Falta SHA256SUMS.txt')
for line in checks.read_text().splitlines():
    expected, name = line.split('  ', 1)
    if hashlib.sha256((root/name).read_bytes()).hexdigest() != expected:
        raise SystemExit('Checksum diferente: ' + name)
print('Higiene de ficheiros, links locais e checksums: OK')
