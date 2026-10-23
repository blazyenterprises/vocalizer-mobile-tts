from pathlib import Path
import zipfile,shutil,ast,hashlib,json
root=Path(__file__).resolve().parent;addon=root/'addon'
shutil.copy2(root/'README.txt',addon/'README.txt')
for p in addon.rglob('*.py'):
 if 'vendor' not in p.parts and 'runtime' not in p.parts:ast.parse(p.read_text(encoding='utf-8'))
out=root/'dist/0.1.1';out.mkdir(parents=True,exist_ok=True)
pkg=out/'vocalizerMobileTTS-0.1.1.nvda-addon'
with zipfile.ZipFile(pkg,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(addon.rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':z.write(p,p.relative_to(addon))
with zipfile.ZipFile(pkg) as z:
 assert z.testzip() is None
 for p in ['manifest.ini','synthDrivers/motorolaV860/__init__.py','engine/runtime/python.exe','engine/worker.py','engine/firmware.bin','engine/ffmpeg.exe']:assert p in z.namelist()
shutil.copy2(root/'README.txt',out/'README.txt')
(out/'provenance.json').write_text(json.dumps(dict(firmware_sha256=hashlib.sha256((addon/'engine/firmware.bin').read_bytes()).hexdigest(),addon_sha256=hashlib.sha256(pkg.read_bytes()).hexdigest(),size=pkg.stat().st_size),indent=2))
print(pkg, pkg.stat().st_size)
