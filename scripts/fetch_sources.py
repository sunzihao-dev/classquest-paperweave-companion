"""Fetch only manifest-listed source PDFs and require the recorded bytes."""
from pathlib import Path
import hashlib
import json
import urllib.request

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root/'experiments/paperweave_source_manifest.json').read_text())
manifest.update(json.loads((root/'experiments/paperweave_extension_manifest.json').read_text()))
out = root/'literature'
out.mkdir(exist_ok=True)
for name, source in manifest.items():
    path = out/f'{name}.pdf'
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256']:
        print(f'{name}: existing hash matches')
        continue
    request = urllib.request.Request(source['url'], headers={'User-Agent':'ResearchCompanion/1.0'})
    with urllib.request.urlopen(request, timeout=45) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != source['sha256']:
        raise RuntimeError(f'{name}: downloaded bytes do not match the pinned source; existing file left unchanged')
    path.write_bytes(data)
    print(f'{name}: downloaded and hash checked')
