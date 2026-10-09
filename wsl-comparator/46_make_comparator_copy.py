"""Plan step 3d: make the comparator copies of our Lemma 3 code as two OAI-tree modules.

Writes lean-checks/comparator-copy/PaperLemma3/Lemma3.lean and Bridge.lean:
- Lemma3.lean: lean-checks/Lemma3.lean through `end Lemma3`, without the trailing #print/#check lines.
- Bridge.lean: the "Corollary 4 from Lemma 3" and "Bridge" parts of lean-checks/Lemma3Bridged.lean
  (from that heading through `end Lemma3`), with the same `open`/namespace/section header, importing
  only Mathlib, the Lemma3 module and Structure.InvariantJetLinearMap. No #find_deps, #print, #check
  or #reroute.
Usage: python -I wsl-comparator/46_make_comparator_copy.py <siegel project root>
"""
import os, re, sys, hashlib

root = sys.argv[1]
lc = os.path.join(root, 'lean-checks')
out = os.path.join(lc, 'comparator-copy', 'PaperLemma3')
os.makedirs(out, exist_ok=True)

l3 = open(os.path.join(lc, 'Lemma3.lean'), encoding='utf-8').read().split('\n')
end = max(i for i, l in enumerate(l3) if l.startswith('end Lemma3'))
lemma3 = '\n'.join(l3[:end + 1]) + '\n'
assert l3[0] == 'import Mathlib' and not any(l.startswith('import') for l in l3[1:end])
assert not any(re.match(r'#[a-z_]', l) for l in l3[:end + 1])  # no #print/#check/... commands

br = open(os.path.join(lc, 'Lemma3Bridged.lean'), encoding='utf-8').read().split('\n')
# the first 988 lines of Lemma3Bridged are Lemma3.lean's body (plus `import ...Main`)
a = next(i for i, l in enumerate(br) if l.startswith('/-! ## Corollary 4 from Lemma 3'))
b = next(i for i, l in enumerate(br) if l.startswith('end Lemma3'))
body = br[a:b + 1]
assert not any(re.match(r'#[a-z_]', l) or 'reroute' in l or 'find_deps' in l for l in body)
header = [
    'import Mathlib',
    'import OAI.NumberTheory.SiegelZeros.PaperLemma3.Lemma3',
    'import OAI.NumberTheory.SiegelZeros.Structure.InvariantJetLinearMap',
    '',
    '/-!',
    '# Corollary 4 and the bridge to OAI\'s `actual_biquadratic_rectangle_span`, via the paper\'s Lemma 3',
    '',
    f'Copied from the Siegel-zero verification project, lean-checks/Lemma3Bridged.lean lines {a + 1}-{b + 1}',
    '(proofs only). `Lemma3.actual_biquadratic_rectangle_span_via_lemma3` has exactly the type of',
    'OAI\'s `actual_biquadratic_rectangle_span` (via `type_of%`) and is proved without OAI\'s',
    'multiplicity estimate.',
    '-/',
    '',
    'open MvPolynomial Pointwise',
    '',
    'namespace Lemma3',
    '',
    'noncomputable section',
    '',
]
bridge = '\n'.join(header + body) + '\n'
for name, text in [('Lemma3.lean', lemma3), ('Bridge.lean', bridge)]:
    p = os.path.join(out, name)
    open(p, 'w', encoding='utf-8', newline='\n').write(text)
    print(f'{os.path.relpath(p, root)}: {text.count(chr(10))} lines, sha256 {hashlib.sha256(text.encode()).hexdigest()}')
