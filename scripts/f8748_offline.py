#!/usr/bin/env python3
"""Descodificador local de formatos F8748. Nao usa a rede.

Recuperacao autorizada. Os dados privados devem ficar fora do repositorio.
Nao imprime passwords, chaves, MACs nem identificadores GPON.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zlib

MAGIC = bytes.fromhex('01020304')
os.umask(0o077)

def save(path, data):
    """Gravacao atomica, privada e sem seguir um link simbolico no destino."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError('Recusado destino simbolico')
    if isinstance(data, (dict, list)):
        data = json.dumps(data, ensure_ascii=False, indent=2).encode()
    if isinstance(data, str):
        data = data.encode()
    fd, name = tempfile.mkstemp(prefix='.f8748-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        os.chmod(name, 0o600)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)

def aes(data, key, iv):
    return subprocess.run(
        ['openssl', 'enc', '-d', '-aes-256-cbc', '-K', key.hex(),
         '-iv', iv.hex(), '-nopad'], input=data, capture_output=True,
        check=True).stdout

def unpad(data):
    if data and 1 <= data[-1] <= 16:
        n = data[-1]
        if data.endswith(bytes([n]) * n):
            return data[:-n]
    return data

def tags(path, vid):
    blob = Path(path).read_bytes()
    if not blob.startswith(b'TAGH'):
        raise ValueError('paramtag sem cabecalho TAGH')
    material = ('zx279132' + str(vid) +
                '8cc72b05705d5c46f412af8cbed55aad')[:32].encode()
    key = hashlib.sha256(material).digest()
    pos, result = 20, {}
    while pos + 10 <= len(blob):
        pid, _, size, f6, f8 = struct.unpack_from('<HHHHH', blob, pos)
        if size > 4096 or pos + 10 + size - size % 16 > len(blob):
            raise ValueError('Registo paramtag truncado ou demasiado grande')
        if f6 == 0 and f8 == 1 and size >= 16:
            ct = blob[pos + 10:pos + 10 + size - size % 16]
            if len(ct) % 16 == 0:
                raw = unpad(aes(ct, key, key[:16])).split(b'\0')[0]
                match = re.match(rb'[a-fA-F0-9]*', raw).group()
                value = (bytes.fromhex(match[:len(match)//2*2].decode())
                         if len(match) >= 2 else raw)
                result[hex(pid)] = value
        nxt = (pos + size + 9) & ~3
        if nxt <= pos:
            break
        pos = nxt
    return result

def catalogues(flash, seed):
    blob = Path(flash).read_bytes()
    line = Path(seed).read_text().strip()
    if len(line) < 64:
        raise ValueError('Seed demasiado curta')
    material = bytes((ord(c)+2) % 256 for c in line[47:63])
    material = (material + line[64:].encode())[:32]
    key = hashlib.sha256(material).digest()
    iv = hashlib.sha256(bytes((ord(c)+3) % 256
                              for c in line[2:34])).digest()[:16]
    found = []
    for match in re.finditer(rb'\x78[\x01\x5e\x9c\xda]', blob):
        try:
            obj = zlib.decompressobj()
            raw = obj.decompress(blob[match.start():match.start()+65536],
                                 2*1024*1024)
        except zlib.error:
            continue
        if not raw.startswith(MAGIC) or len(raw) < 72:
            continue
        size = struct.unpack_from('>I', raw, 64)[0]
        if size < 16 or size % 16 or size > len(raw)-72:
            continue
        try:
            plain = unpad(aes(raw[72:72+size], key, iv)).decode()
        except (UnicodeDecodeError, subprocess.CalledProcessError):
            continue
        entries = {}
        for row in plain.splitlines():
            if '=' in row:
                name, val = row.split('=', 1)
                if re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', name):
                    entries[name] = val.strip('\r\0')
        if entries:
            found.append({'offset': match.start(), 'entries': entries})
    if not found:
        raise ValueError('Sem catalogos decifrados nas janelas recolhidas')
    return found

def unpack_xml(raw):
    if not raw.startswith(MAGIC + b'\0\0\0\0'):
        raise ValueError('Contentor interior diferente do tipo 0 observado')
    pos, parts = 60, []
    total = 0
    while pos + 12 <= len(raw):
        size, compressed, more = struct.unpack_from('>III', raw, pos)
        pos += 12
        total += size
        if size > 16*1024*1024 or total > 64*1024*1024:
            raise ValueError('Limite local de descompressao excedido')
        if compressed > len(raw)-pos:
            raise ValueError('Bloco comprimido incompleto')
        obj = zlib.decompressobj()
        part = obj.decompress(raw[pos:pos+compressed], size+1)
        if len(part) != size or not obj.eof:
            raise ValueError('Tamanho ou integridade zlib incorretos')
        parts.append(part)
        pos += compressed
        if not more:
            xml = b''.join(parts)
            ET.fromstring(xml)
            return xml
    raise ValueError('Contentor interior incompleto')

def decode_config(cfg, values, cats):
    cfg = Path(cfg).read_bytes()
    if len(cfg) < 88 or cfg[:8] != MAGIC + b'\0\0\0\x06':
        raise ValueError('Configuracao diferente do tipo 6 observado')
    plain_len, cipher_len, _ = struct.unpack_from('>III', cfg, 60)
    if (cipher_len < 16 or cipher_len % 16 or cipher_len > len(cfg)-72
            or plain_len > cipher_len):
        raise ValueError('Configuracao cifrada incompleta')
    cat = next((x['entries'] for x in cats
                if 'DefAESCBCIV' in x['entries']), {})
    serials = set()
    for tag in ('0x200', '0x880', '0x881', '0x883'):
        value = values.get(tag, b'')
        if value:
            serials.add(value.hex())
            try:
                text = value.decode()
                if text.isprintable():
                    serials.add(text)
            except UnicodeDecodeError:
                pass
    vendor, serial = values.get('0x880', b''), values.get('0x881', b'')
    if vendor and serial:
        for value in (vendor+serial, vendor+serial.hex().encode()):
            try:
                text = value.decode()
                if text.isprintable():
                    serials.add(text)
            except UnicodeDecodeError:
                pass
    macs = {values[t] for t in ('0x100','0x101','0x102','0x103','0x104','0x300')
            if len(values.get(t, b'')) == 6}
    if not serials or not macs:
        raise ValueError('Faltam identificadores binarios do dispositivo')
    ivs = {'ZTE%FN$GponNJ025'}
    if cat.get('DefAESCBCIV'):
        ivs.add(cat['DefAESCBCIV'])
    for serial in sorted(serials):
        for mac in sorted(macs):
            for mac_text in (mac.hex(), mac[::-1].hex()):
                for serial_text in (serial, serial[4:]):
                    for iv_text in sorted(ivs):
                        key = hashlib.sha256((serial_text+mac_text).encode()).digest()
                        iv = hashlib.sha256(iv_text.encode()).digest()[:16]
                        if aes(cfg[72:88], key, iv)[:8] != MAGIC+b'\0\0\0\0':
                            continue
                        raw = aes(cfg[72:72+cipher_len], key, iv)[:plain_len]
                        try:
                            return unpack_xml(raw)
                        except (ValueError, zlib.error, ET.ParseError):
                            continue
    raise ValueError('Sem chave valida nas derivacoes limitadas do equipamento')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='cmd', required=True)
    log = sub.add_parser('log')
    log.add_argument('--input', required=True)
    log.add_argument('--output', required=True)
    for name in ('admin', 'pppoe'):
        p = sub.add_parser(name)
        p.add_argument('--dir', required=True)
        p.add_argument('--vid', type=int, default=108)
        p.add_argument('--credentials', required=True)
        if name == 'pppoe':
            p.add_argument('--username', required=True)
    args = parser.parse_args()
    if args.cmd == 'log':
        text = Path(args.input).read_text(errors='replace')
        start = text.find("hexdump -ve")
        if start < 0:
            raise ValueError('Sem comando hexdump no log')
        tail = text[start:]
        rows = []
        for line in tail.splitlines()[1:]:
            line = line.strip()
            if line.startswith('/ #'):
                break
            if re.fullmatch(r'(?:[0-9a-fA-F]{2}){1,16}', line):
                rows.append(line)
        data = bytes.fromhex(''.join(rows))
        if not data.startswith(MAGIC):
            raise ValueError('Sem contentor ZTE completo no log')
        save(args.output, data)
        print('Configuracao binaria reconstruida; bytes:', len(data))
        return
    root = Path(args.dir)
    values = tags(root/'paramtag.bin', args.vid)
    dest = Path(args.credentials)
    result = json.loads(dest.read_text()) if dest.exists() else {}
    if args.cmd == 'admin':
        username = values.get('0x602', b'admin').decode().strip()
        password = values.get('0x702', b'').decode()
        if not username or not password:
            raise ValueError('Tags admin incompletas; usar decrypt da ferramenta base')
        result.update(username=username, password=password,
                      url='http://192.168.1.1/',
                      verification='Extraido de paramtag; validar login no painel')
    else:
        cats = catalogues(root/'flash-windows.bin', root/'hardcode.seed')
        save(root/'hardcode-catalogues.json', cats)
        xml = decode_config(root/'db_user_cfg.xml', values, cats)
        save(root/'plain-config.xml', xml)
        matches = []
        for row in ET.fromstring(xml).iter('Row'):
            fields = {dm.attrib.get('name'): dm.attrib.get('val', '')
                      for dm in row.findall('DM')}
            if fields.get('Username') == args.username:
                matches.append(fields)
        if len(matches) != 1 or not matches[0].get('Password', '').strip():
            raise ValueError('Nao existe um unico registo PPP completo para esse username')
        result['pppoe'] = dict(username=args.username,
                              password=matches[0]['Password'],
                              verification='Extraido do mesmo registo PPP; sem teste de autenticacao')
    save(dest, result)
    print('Credenciais guardadas com permissoes 0600; nenhum segredo impresso.')

if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError, ET.ParseError,
            zlib.error, KeyError, struct.error) as exc:
        raise SystemExit('Falha local: ' + type(exc).__name__ + '. Rever ficheiros e formato.')
