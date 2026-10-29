"""Fixtures artificiais criadas localmente; nunca contacta equipamento."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zlib

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('f8748_offline', ROOT/'scripts/f8748_offline.py')
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)


def encrypt(data, key, iv):
    return subprocess.run(['openssl','enc','-e','-aes-256-cbc','-K',key.hex(),
                           '-iv',iv.hex(),'-nopad'],input=data,capture_output=True,
                          check=True).stdout


def pad(data):
    size = 16-len(data)%16
    return data+bytes([size])*size


def paramtag(values):
    key = hashlib.sha256(('zx279132108'+'8cc72b05705d5c46f412af8cbed55aad')[:32].encode()).digest()
    blob = bytearray(b'TAGH'+b'\0'*16)
    for tag, value in values.items():
        ct = encrypt(pad(value.hex().encode()),key,key[:16])
        pos = len(blob)
        size = len(ct)+4
        blob += struct.pack('<HHHHH',tag,0,size,0,1)+ct
        target = (pos+size+9)&~3
        blob += b'\0'*(target-len(blob))
    return bytes(blob)


def fixture(folder, duplicate=False):
    # These are intentionally fictitious values, not identifiers of a unit.
    values = {0x100:bytes.fromhex('0299aabbccdd'),0x881:b'TEST0001',
              0x702:b'synthetic-admin'}
    (folder/'paramtag.bin').write_bytes(paramtag(values))
    seed = '0123456789abcdef'*4+'v1.0'
    (folder/'hardcode.seed').write_text(seed)
    ivtext = 'synthetic-iv'
    plain = ('DefAESCBCKey=unused\nDefAESCBCIV='+ivtext+'\n').encode()
    material = (bytes((ord(c)+2)%256 for c in seed[47:63])+seed[64:].encode())[:32]
    key = hashlib.sha256(material).digest()
    iv = hashlib.sha256(bytes((ord(c)+3)%256 for c in seed[2:34])).digest()[:16]
    ct = encrypt(pad(plain),key,iv)
    header = bytearray(72);header[:8]=f.MAGIC+b'\0\0\0\x02'
    struct.pack_into('>III',header,60,len(plain),len(ct),0)
    (folder/'flash-windows.bin').write_bytes(b'noise'+zlib.compress(bytes(header)+ct))
    tree = ET.Element('ZTE');table = ET.SubElement(tree,'Table',name='WANCPPP')
    for _ in range(2 if duplicate else 1):
        row = ET.SubElement(table,'Row')
        ET.SubElement(row,'DM',name='Username',val='synthetic@example.invalid')
        ET.SubElement(row,'DM',name='Password',val='synthetic-pppoe')
    xml = ET.tostring(tree)
    compressed = zlib.compress(xml)
    inner = f.MAGIC+b'\0\0\0\0'+b'\0'*52
    inner += struct.pack('>III',len(xml),len(compressed),0)+compressed
    key = hashlib.sha256((values[0x881].decode()+values[0x100][::-1].hex()).encode()).digest()
    iv = hashlib.sha256(ivtext.encode()).digest()[:16]
    ct = encrypt(pad(inner),key,iv)
    header = bytearray(72);header[:8]=f.MAGIC+b'\0\0\0\x06'
    struct.pack_into('>III',header,60,len(inner),len(ct),0)
    cfg=bytes(header)+ct
    (folder/'db_user_cfg.xml').write_bytes(cfg)
    return values,xml,cfg


class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.values,self.xml,self.cfg=fixture(self.folder)

    def tearDown(self):
        self.temp.cleanup()

    def cli(self,*args,ok=True):
        result=subprocess.run([sys.executable,str(ROOT/'scripts/f8748_offline.py'),*args],
                              capture_output=True,text=True)
        self.assertEqual(result.returncode==0,ok,result.stderr)
        self.assertNotIn('synthetic-admin',result.stdout+result.stderr)
        self.assertNotIn('synthetic-pppoe',result.stdout+result.stderr)
        return result

    def test_binary_tags_and_catalogue_big_endian(self):
        values=f.tags(self.folder/'paramtag.bin',108)
        self.assertEqual(values['0x100'],self.values[0x100])
        cats=f.catalogues(self.folder/'flash-windows.bin',self.folder/'hardcode.seed')
        self.assertEqual(cats[0]['entries']['DefAESCBCIV'],'synthetic-iv')
        self.assertEqual(f.decode_config(self.folder/'db_user_cfg.xml',values,cats),self.xml)

    def test_cli_preserves_admin_and_private_permissions(self):
        target=str(self.folder/'credentials.json')
        self.cli('admin','--dir',str(self.folder),'--credentials',target)
        self.cli('pppoe','--dir',str(self.folder),'--username','synthetic@example.invalid',
                 '--credentials',target)
        data=json.loads(Path(target).read_text())
        self.assertEqual(data['password'],'synthetic-admin')
        self.assertEqual(data['pppoe']['password'],'synthetic-pppoe')
        self.assertEqual(stat.S_IMODE(Path(target).stat().st_mode),0o600)

    def test_wrong_account_preserves_existing_file(self):
        target=self.folder/'credentials.json';target.write_text('{"preserve": true}')
        before=target.read_bytes()
        self.cli('pppoe','--dir',str(self.folder),'--username','wrong@example.invalid',
                 '--credentials',str(target),ok=False)
        self.assertEqual(target.read_bytes(),before)

    def test_duplicate_account_is_rejected(self):
        fixture(self.folder,duplicate=True)
        target=self.folder/'credentials.json'
        self.cli('pppoe','--dir',str(self.folder),'--username','synthetic@example.invalid',
                 '--credentials',str(target),ok=False)
        self.assertFalse(target.exists())

    def test_hexdump_retains_partial_line_and_trailing_spaces(self):
        data=self.cfg+b'\0'*5
        rows=[data[i:i+16].hex()+'  ' for i in range(0,len(data),16)]
        log=self.folder/'session.log'
        log.write_text('/ # hexdump -ve example\n'+'\n'.join(rows)+'\n/ # \n')
        target=self.folder/'reconstructed.xml'
        self.cli('log','--input',str(log),'--output',str(target))
        self.assertEqual(target.read_bytes(),data)

    def test_truncated_configuration_and_symbolic_output(self):
        path=self.folder/'db_user_cfg.xml';path.write_bytes(self.cfg[:-1])
        values=f.tags(self.folder/'paramtag.bin',108)
        with self.assertRaises(ValueError):f.decode_config(path,values,[])
        link=self.folder/'link';link.symlink_to(self.folder/'missing')
        with self.assertRaises(ValueError):f.save(link,b'no')
        self.assertFalse((self.folder/'missing').exists())

    def test_collector_is_reproducible(self):
        for name in ('preparar_coletor.py','recuperar-admin-f8748.sh'):
            shutil.copy(ROOT/'scripts'/name,self.folder/name)
        subprocess.run([sys.executable,str(self.folder/'preparar_coletor.py')],
                       check=True,capture_output=True)
        self.assertEqual((self.folder/'recolher-pppoe-f8748.sh').read_bytes(),
                         (ROOT/'scripts/recolher-pppoe-f8748.sh').read_bytes())


if __name__=='__main__':
    unittest.main()
