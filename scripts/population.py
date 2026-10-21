"""Paper prep 2, Task 1: replay population against the configs formalization.yaml references (read-only).

Usage: python -I scripts/population.py <repo root> <formalization.yaml at fd4aeeb> <formalization.yaml at adc7f12>
Stage membership comes from the raw per-config logs (same file set as scripts/recount.py, final runs only).
The yaml is parsed by regex on `comparator_config:` lines (no PyYAML here); the count is checked against the
2026-10-11 main plan (results/2026-10-11-corpus-mainplan.txt: "distinct configs 189").
"""
import collections, hashlib, os, re, sys

root, y_fd, y_adc = sys.argv[1:4]
res = os.path.join(root, 'results')
pat = re.compile(r'^([A-Za-z0-9]+)-(nanoda|shipped)\.log$')  # final runs only (no .stopped/.interrupted suffix)


def configs_in(d):
    return {m.group(1) for f in os.listdir(d) if (m := pat.match(f))}


stages = {'pilot (adc7f12)': configs_in(os.path.join(res, '2026-10-11-corpus-pilot')),
          'headline (fd4aeeb)': configs_in(os.path.join(res, '2026-10-11-corpus-headline'))}
rem = os.path.join(res, '2026-10-12-corpus-remainder')
stages['remainder (fd4aeeb)'] = set().union(*(configs_in(os.path.join(rem, b)) for b in sorted(os.listdir(rem)) if b.startswith('batch-')))
# the headline dir also holds shipped runs of sampled pilot configs (75_headline_batch.sh); count them separately
pilot_shipped_in_headline = stages['headline (fd4aeeb)'] & stages['pilot (adc7f12)']


def referenced(path):
    txt = open(path, encoding='utf-8').read()
    return {m.group(1).split('/')[-1][:-5] for m in re.finditer(r'comparator_config:\s*["\']?([^\s"\']+)', txt)}, \
        hashlib.sha256(txt.encode('utf-8')).hexdigest()


ref_fd, h_fd = referenced(y_fd)
ref_adc, h_adc = referenced(y_adc)
print(f'formalization.yaml fd4aeeb sha256 {h_fd}: {len(ref_fd)} distinct referenced configs')
print(f'formalization.yaml adc7f12 sha256 {h_adc}: {len(ref_adc)} distinct referenced configs')

print('\n== stage totals (configs with a final nanoda or shipped run in that stage)')
for s, c in stages.items():
    print(f'{s}: {len(c)}')
print(f'sum of stage totals: {sum(map(len, stages.values()))}')
print(f'headline dir also holds shipped-only runs of pilot configs: {sorted(pilot_shipped_in_headline)}')

where = collections.defaultdict(list)
for s, c in stages.items():
    for n in c:
        where[n].append(s)
multi = {n: v for n, v in where.items() if len(v) > 1}
print(f'\n== configs in more than one stage: {len(multi)}')
for n in sorted(multi):
    print(f'{n}\t' + ', '.join(multi[n]))
allc = set(where)
fd = stages['headline (fd4aeeb)'] | stages['remainder (fd4aeeb)']
fd_nanoda = fd - (pilot_shipped_in_headline - stages['remainder (fd4aeeb)'])
print(f'\ndistinct configs over all stages: {len(allc)}')
print(f'distinct configs with an fd4aeeb run: {len(fd)}; excluding shipped-only runs of pilot configs: {len(fd_nanoda)}')

print('\n== replay vs referenced (fd4aeeb yaml)')
print(f'replayed (any stage) and referenced: {len(allc & ref_fd)}')
print(f'replayed but NOT referenced at fd4aeeb: {sorted(allc - ref_fd)}')
print(f'referenced at fd4aeeb but NOT replayed in any stage: {sorted(ref_fd - allc)}')
print(f'referenced but with no fd4aeeb nanoda run (covered by the pilot at adc7f12 only): {sorted(ref_fd - fd_nanoda)}')
print(f'pilot configs referenced at adc7f12: {sorted(stages["pilot (adc7f12)"] & ref_adc)}; not referenced at adc7f12: {sorted(stages["pilot (adc7f12)"] - ref_adc)}')

print('\n== the two referenced sets (where "178" comes from)')
print(f'referenced at adc7f12: {len(ref_adc)}; at fd4aeeb: {len(ref_fd)}; in both: {len(ref_adc & ref_fd)}')
print(f'referenced at adc7f12 but not at fd4aeeb: {sorted(ref_adc - ref_fd)}')
print(f'referenced at fd4aeeb but not at adc7f12 ({len(ref_fd - ref_adc)}): {sorted(ref_fd - ref_adc)}')
print(f'adc7f12-referenced configs missing from the replay: {sorted(ref_adc - allc)}')
print(f'fd4aeeb-replayed configs (187) that adc7f12 references: {len(fd & ref_adc)}; that only fd4aeeb references: {len(fd - ref_adc)}')
