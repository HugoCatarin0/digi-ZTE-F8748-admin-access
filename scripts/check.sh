#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v python3 >/dev/null
command -v openssl >/dev/null
bash -n scripts/recuperar-admin-f8748.sh
bash -n scripts/recolher-pppoe-f8748.sh
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
