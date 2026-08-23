"""Dump candidate marks to JSON for the Node/playwright preview."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import breath_rosette as br  # noqa: E402


def dump(specs, out):
    data = []
    for name, spec in specs:
        r = br.build(spec)
        try:
            line = br.check(name, r)
            ok = True
        except AssertionError as e:
            line, ok = f'FAIL {e}', False
        f = r['fit']
        data.append(dict(
            name=name, ok=ok, note=line,
            paths=[[' '.join(br.to_paths(p)), fill] for p, fill in r['layers']],
            key=spec['palette'][0],
            face=dict(cy=f['cy'], size=f['size'], gap=f['gap']) if f else None,
        ))
        print(line)
    Path(out).write_text(json.dumps(data, indent=1))
    return data
