#!/usr/bin/env python3
"""Gera um coletor PPPoE a partir da copia administrativa incluida."""
from pathlib import Path

root = Path(__file__).resolve().parent
src = (root / 'recuperar-admin-f8748.sh').read_text()
needle = 'if [ -n "$SEED" ] && [ -s "$OUTDIR/oss.bin" ]; then return 0; fi'
replacement = ('if [ -n "$SEED" ] && [ -s "$OUTDIR/oss.bin" ]; then '
               'cp "$T/flash.bin" "$OUTDIR/flash-windows.bin"; return 0; fi')
assert src.count(needle) == 1, 'Base diferente da copia incluida'
src = src.replace(needle, replacement)
marker = '# --------------------------------- dispatcher --------------------------------'
assert src.count(marker) == 1
override = r'''
# Variante documental: junta leituras previstas pelo procedimento.
# Nao grava flash nem altera perfis WAN. Cria temporarios em /var/tmp.
dump_all(){
  printf 'cat /proc/capability/boardtype\n' > "$T/board-commands"
  ssh_session "$T/board-commands" "$T/board.log" || true
  grep -aE '^(type|flag|vid|cpuname)' "$T/board.log" | head -8 > "$OUTDIR/boardtype.txt" || true
  get_paramtag
  printf '%s\n' "hexdump -ve '16/1 \"%02x\" \"\\n\"' /userconfig/cfg/db_user_cfg.xml" > "$T/config-commands"
  ssh_session "$T/config-commands" "$OUTDIR/ppp-config-session.log" || true
  get_hardcode
}

'''
dst = root / 'recolher-pppoe-f8748.sh'
dst.write_text(src.replace(marker, override + marker))
dst.chmod(0o700)
print('Coletor gerado. Rever antes de executar; sem contacto com o router nesta etapa.')
