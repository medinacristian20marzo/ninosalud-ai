"""Verify files in the immutable release manifest. Standard library only."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def main():
    path=ROOT/'SHA256SUMS.json'
    if not path.exists():
        print('Missing SHA256SUMS.json', file=sys.stderr); return 2
    expected=json.loads(path.read_text())['files']; errors=[]
    for name,digest in expected.items():
        file=(ROOT/name).resolve()
        if not file.is_relative_to(ROOT):
            errors.append(name+': invalid manifest path'); continue
        if not file.is_file():
            errors.append(name+': missing'); continue
        if hashlib.sha256(file.read_bytes()).hexdigest()!=digest: errors.append(name+': changed')
    if errors:
        print('\n'.join(errors)); return 1
    print(f'PASS: {len(expected)} release files match SHA-256 checksums.')
    print('Generated outputs and additional unlisted local files are not checked.')
    return 0
if __name__=='__main__':raise SystemExit(main())
