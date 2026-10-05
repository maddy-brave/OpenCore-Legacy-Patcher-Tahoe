"""Compare two OCLP EFI build manifests (sha256sum or shasum format) and plist-diff any mismatched plists.
Usage: python compare-manifests.py <manifest-A> <tree-A> <manifest-B> <tree-B>
Manifest lines look like '<hash>  ./path' or '<hash> *./path'; both are accepted.
Exit 0 when every file matches apart from config.plist's #Revision:Build-Version; 1 otherwise.
"""
import plistlib
import sys
from pathlib import Path

IGNORED_PLIST_KEYS = {("#Revision", "Build-Version")}


def load_manifest(path: Path) -> dict[str, str]:
    out = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        digest, _, rest = line.partition(" ")
        rel = rest.lstrip(" *").lstrip()
        if rel.startswith("./"):
            rel = rel[2:]
        out[rel.replace("\\", "/")] = digest.lower()
    return out


def flatten(obj, prefix=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from flatten(v, prefix + (str(k),))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from flatten(v, prefix + (f"[{i}]",))
    else:
        yield prefix, obj


def plist_diff(a: Path, b: Path) -> list[str]:
    da = dict(flatten(plistlib.load(a.open("rb"))))
    db = dict(flatten(plistlib.load(b.open("rb"))))
    lines = []
    for key in sorted(set(da) | set(db), key=lambda k: "/".join(k)):
        if key in IGNORED_PLIST_KEYS:
            continue
        va, vb = da.get(key, "<absent>"), db.get(key, "<absent>")
        if va != vb:
            lines.append(f"    {'/'.join(key)}: A={va!r} B={vb!r}")
    return lines


def main() -> int:
    ma, ta, mb, tb = (Path(p) for p in sys.argv[1:5])
    a, b = load_manifest(ma), load_manifest(mb)
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    common = sorted(set(a) & set(b))
    same = [p for p in common if a[p] == b[p]]
    differ = [p for p in common if a[p] != b[p]]
    print(f"A: {len(a)} files  B: {len(b)} files  common: {len(common)}  identical: {len(same)}  differ: {len(differ)}")
    print(f"only in A: {len(only_a)}  only in B: {len(only_b)}")
    for p in only_a:
        print(f"  only A: {p}")
    for p in only_b:
        print(f"  only B: {p}")
    benign = 0
    for p in differ:
        print(f"  DIFF {p}")
        fa, fb = ta / p, tb / p
        if p.endswith(".plist") and fa.exists() and fb.exists():
            d = plist_diff(fa, fb)
            if not d:
                print("    plist content identical apart from ignored keys (byte difference is formatting or build date)")
                benign += 1
            else:
                print("\n".join(d))
        elif fa.exists() and fb.exists():
            ba, bb = fa.read_bytes(), fb.read_bytes()
            print(f"    sizes A={len(ba)} B={len(bb)}; CR bytes A={ba.count(b'\r')} B={bb.count(b'\r')}")
            if ba.replace(b"\r\n", b"\n") == bb.replace(b"\r\n", b"\n"):
                print("    identical after CRLF normalisation")
    verdict = not only_a and not only_b and len(differ) == benign
    print("VERDICT:", "PARITY (only build-date or formatting differences)" if verdict else "MISMATCH")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
