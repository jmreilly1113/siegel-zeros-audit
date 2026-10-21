"""Compare the Zenodo-archived zip of reviewer-packet-v3 with `git archive reviewer-packet-v3` (read-only).

Usage: python -I compare_v3_archive.py <zip> <extracted git archive dir> <expected zip md5>
Ignores only the zip's top-level directory name. Compares the set of file paths and the sha256 of every file.
"""
import hashlib, os, sys, zipfile

zpath, tdir, md5_expected = sys.argv[1:4]
sys.stdout.reconfigure(encoding='utf-8', newline='\n')
md5 = hashlib.md5(open(zpath, 'rb').read()).hexdigest()
print(f'zip: {os.path.getsize(zpath)} bytes, md5 {md5} (record checksum md5:{md5_expected}: {"MATCH" if md5 == md5_expected else "MISMATCH"})')
print(f'zip sha256 {hashlib.sha256(open(zpath, "rb").read()).hexdigest()}')
z = zipfile.ZipFile(zpath)
names = [i for i in z.infolist() if not i.is_dir()]
tops = {i.filename.split('/', 1)[0] for i in z.infolist()}
print(f'zip top-level directories: {sorted(tops)}')
zfiles = {}
for i in names:
    rel = i.filename.split('/', 1)[1]
    zfiles[rel] = hashlib.sha256(z.read(i)).hexdigest()
tfiles = {}
for dp, dns, fs in os.walk(tdir):
    for f in fs:
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, tdir).replace(os.sep, '/')
        tfiles[rel] = hashlib.sha256(open(p, 'rb').read()).hexdigest()
only_z = sorted(set(zfiles) - set(tfiles)); only_t = sorted(set(tfiles) - set(zfiles))
diff = sorted(k for k in set(zfiles) & set(tfiles) if zfiles[k] != tfiles[k])
print(f'files: zip {len(zfiles)}, git archive {len(tfiles)}')
print(f'only in zip: {only_z or "none"}')
print(f'only in git archive: {only_t or "none"}')
print(f'same path, different content: {diff or "none"}')
print('RESULT: ' + ('IDENTICAL file tree and contents (top-level directory name ignored)' if not (only_z or only_t or diff) else 'DIFFERENT'))
need = ['README.md', 'CITATION.cff', '.zenodo.json', 'docs/effectivity/note-v2.pdf',
        'docs/effectivity/derivation-banks-device.md', 'src/effectivity_banks_device.py',
        'results/2026-10-20-effectivity-device/device-output.txt']
for n in need:
    print(f'  contains {n}: {n in zfiles}')
print(f'  contains local/outreach-facts.md: {"local/outreach-facts.md" in zfiles}; any path under local/: {any(k.startswith("local/") for k in zfiles)}')
print(f'  contains refs/banks-2610.15483v1.pdf or .tex: {any(k.startswith("refs/banks-2610.15483v1.") for k in zfiles)}')
