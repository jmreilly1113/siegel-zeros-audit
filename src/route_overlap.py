"""Declaration overlap between the proof routes of the Siegel-zero formalization (task 8.7, issue #40).

Exact set operations on constant-name lists produced by wsl-comparator/56_closure_names.py from lean4export
dumps. Two conventions are reported: the full dump set (every declaration lean4export wrote) and the
referenced-only set (the #find_deps closure). The split by name prefix is approximate: a name's prefix is not
its defining package, and the dumps do not record defining modules,
except that private names (`_private.<Module>.<n>.<decl>`) spell out their defining module; those are
classified by that module.

Usage:
  python src/route_overlap.py <names dir> <pnt names .txt.gz>
The names dir must hold <label>.full.txt.gz and <label>.referenced.txt.gz for the labels route1,
route2-original, route2-rerouted, mainrerouted-challenge and lemma3-bridge.
"""
import gzip
import os
import re
import sys
from collections import Counter
from fractions import Fraction

CORE_TOPS = {
    'Init', 'Lean', 'Std', 'Lake',
    'Nat', 'Int', 'List', 'Array', 'Option', 'Bool', 'Prod', 'Sum', 'Fin', 'String', 'Char', 'Substring',
    'UInt8', 'UInt16', 'UInt32', 'UInt64', 'USize', 'Float', 'Float32', 'ByteArray', 'FloatArray',
    'Eq', 'HEq', 'Ne', 'Iff', 'And', 'Or', 'Not', 'True', 'False', 'Exists', 'Decidable', 'Subtype',
    'Sigma', 'PSigma', 'PSum', 'PProd', 'MProd', 'PUnit', 'Unit', 'Empty', 'PEmpty', 'Quot', 'Quotient',
    'Setoid', 'Function', 'Id', 'Thunk', 'Task', 'IO', 'EIO', 'BaseIO', 'EStateM', 'ST', 'Except',
    'ExceptT', 'ReaderT', 'StateT', 'StateRefT', 'OptionT', 'Monad', 'Functor', 'Applicative', 'Bind',
    'Pure', 'Seq', 'SeqLeft', 'SeqRight', 'BitVec', 'Vector', 'Subarray', 'Ordering', 'WellFounded',
    'Acc', 'Classical', 'propext', 'funext', 'HAdd', 'HMul', 'HSub', 'HDiv', 'HMod', 'HPow', 'Add',
    'Mul', 'Sub', 'Div', 'Mod', 'Neg', 'LE', 'LT', 'Max', 'Min', 'OfNat', 'BEq', 'Hashable', 'Inhabited',
    'Nonempty', 'Membership', 'GetElem', 'Coe', 'CoeTail', 'CoeHead', 'CoeOut', 'CoeSort', 'CoeFun',
}
OTHER_PKG_TOPS = {'Aesop', 'Qq', 'Plausible', 'ProofWidgets', 'ImportGraph', 'LeanSearchClient'}
AUTO_COMPONENT = re.compile(
    r'^(_.*|match_\d+|proof_\d+|eq_\d+|eq_def|induct|induct_unfolding|rec|recOn|casesOn|below|brecOn|'
    r'binductionOn|ibelow|noConfusion|noConfusionType|injEq|inj|sizeOf_spec|ctorIdx|toCtorIdx|'
    r'mutual_induct|fun_cases|congr_simp)$')
CATEGORIES = ['core', 'Batteries', 'other packages', 'OAI', 'Lemma3 (ours)', 'PNT patch', 'Mathlib-style',
              'root (no namespace)']


def load(path):
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        return {line.rstrip('\n') for line in f if line.strip()}


def top(name):
    return name.split('.', 1)[0]


def is_auto(name):
    return any(AUTO_COMPONENT.match(c) for c in name.split('.'))


def private_module(name):
    """For a private name `_private.<Module>.<n>.<decl>`, the defining module (as a dotted string)."""
    parts = name.split('.')
    mod = []
    for c in parts[1:]:
        if c.isdigit():
            break
        mod.append(c)
    return '.'.join(mod)


def category(name, pnt):
    if name.startswith('_private.'):
        m = private_module(name)
        if m.startswith('OAI.NumberTheory.SiegelZeros.PaperLemma3') or m.startswith('Lemma3'):
            return 'Lemma3 (ours)'
        if m.startswith('OAI.') or m == 'OAI':
            return 'OAI'
        if m.startswith('PrimeNumberTheoremAnd'):
            return 'PNT patch'
        t = m.split('.', 1)[0]
        if t in ('Init', 'Lean', 'Std', 'Lake'):
            return 'core'
        if t == 'Batteries':
            return 'Batteries'
        if t in OTHER_PKG_TOPS:
            return 'other packages'
        return 'Mathlib-style'
    if name.startswith('OAI.'):
        return 'OAI'
    if name.startswith('Lemma3.'):
        return 'Lemma3 (ours)'
    if name in pnt or top(name) == 'PrimeNumberTheoremAnd':
        return 'PNT patch'
    if '.' not in name:
        return 'root (no namespace)'
    t = top(name)
    if t in CORE_TOPS:
        return 'core'
    if t == 'Batteries':
        return 'Batteries'
    if t in OTHER_PKG_TOPS:
        return 'other packages'
    return 'Mathlib-style'


def pair_stats(a, b):
    inter, union = a & b, a | b
    j = Fraction(len(inter), len(union)) if union else Fraction(0)
    return {'A': len(a), 'B': len(b), 'A&B': len(inter), 'A|B': len(union), 'A-B': len(a - b),
            'B-A': len(b - a), 'jaccard': j}


def split(s, pnt):
    c = Counter(category(n, pnt) for n in s)
    return {k: c.get(k, 0) for k in CATEGORIES}


def fmt_j(j):
    return f'{float(j):.6f}'


def report(names_dir, pnt_path, out=sys.stdout):
    pnt = load(pnt_path)
    labels = {'route1': 'route 1 (exists_absolute_real_zero_gap)',
              'route2-original': 'route 2 original (dirichletRealZeroBound_proof)',
              'route2-rerouted': 'route 2 rerouted (dirichletRealZeroBound_proof, comparator-accepted clone)',
              'mainrerouted-challenge': 'MainRerouted.lean export (challenge_dirichletRealZeroBound_proof)',
              'lemma3-bridge': 'our Lemma 3 code (bridge root)'}
    sets = {conv: {k: load(os.path.join(names_dir, f'{k}.{conv}.txt.gz')) for k in labels}
            for conv in ('referenced', 'full')}
    p = lambda *a: print(*a, file=out)
    p(f'PNT patch names loaded: {len(pnt)}')
    pairs = [('route1', 'route2-original'), ('route1', 'route2-rerouted'), ('route2-original', 'route2-rerouted')]
    for conv in ('referenced', 'full'):
        S = sets[conv]
        p(f'\n######## convention: {conv} ' + ('(#find_deps closure)' if conv == 'referenced' else '(every declaration in the lean4export dump)'))
        p('set sizes: ' + ', '.join(f'{k} {len(v)}' for k, v in S.items()))
        p('\n== pairwise, all names')
        p(f'{"A":<16} {"B":<16} {"|A|":>8} {"|B|":>8} {"|A&B|":>8} {"|A|B|":>8} {"|A-B|":>8} {"|B-A|":>8} {"Jaccard":>9}')
        for x, y in pairs:
            s = pair_stats(S[x], S[y])
            p(f'{x:<16} {y:<16} {s["A"]:>8} {s["B"]:>8} {s["A&B"]:>8} {s["A|B"]:>8} {s["A-B"]:>8} {s["B-A"]:>8} {fmt_j(s["jaccard"]):>9}')
        p('\n== pairwise, without auto-generated names (component matching ' + AUTO_COMPONENT.pattern + ')')
        for x, y in pairs:
            a = {n for n in S[x] if not is_auto(n)}; b = {n for n in S[y] if not is_auto(n)}
            s = pair_stats(a, b)
            p(f'{x:<16} {y:<16} {s["A"]:>8} {s["B"]:>8} {s["A&B"]:>8} {s["A|B"]:>8} {s["A-B"]:>8} {s["B-A"]:>8} {fmt_j(s["jaccard"]):>9}')
        p('auto-generated names per set: ' + ', '.join(f'{k} {sum(map(is_auto, v))}' for k, v in S.items()))
        p('\n== split by name prefix (approximate; prefix is not defining package)')
        p(f'{"set":<34} ' + ' '.join(f'{c[:14]:>14}' for c in CATEGORIES))
        rows = [(k, S[k]) for k in ('route1', 'route2-original', 'route2-rerouted')]
        rows += [(f'{x} & {y}', S[x] & S[y]) for x, y in pairs]
        for k, v in rows:
            sp = split(v, pnt)
            p(f'{k:<34} ' + ' '.join(f'{sp[c]:>14}' for c in CATEGORIES))
        sh = sorted(n for n in S['route1'] & S['route2-original'] if category(n, pnt) == 'OAI')
        p(f'\n== shared OAI names (OAI.* and private names from OAI modules), route1 & route2-original: {len(sh)}')
        for n in sh:
            p('  ' + n)
        sh2 = sorted(n for n in S['route1'] & S['route2-rerouted'] if category(n, pnt) == 'OAI')
        p(f'shared OAI names, route1 & route2-rerouted: {len(sh2)}' + (' (same list)' if sh2 == sh else ''))
        if sh2 != sh:
            for n in sh2:
                p('  ' + n)
        mt = Counter(top(n) if not n.startswith('_private.') else '_private ' + '.'.join(private_module(n).split('.')[:2])
                     for n in S['route1'] & S['route2-original'] if category(n, pnt) == 'Mathlib-style')
        p('\n== 30 largest shared Mathlib-style top-level namespaces, route1 & route2-original'
          ' (private names grouped by the first two components of their defining module)')
        for t, c in mt.most_common(30):
            p(f'  {t:<28} {c:>6}')
        add = S['route2-rerouted'] - S['route2-original']
        rem = S['route2-original'] - S['route2-rerouted']
        p(f'\n== route2-rerouted minus route2-original: {len(add)}; by prefix: {split(add, pnt)}')
        p('   OAI.*/Lemma3.* among them: ' + ', '.join(sorted(n for n in add if category(n, pnt) in ('OAI', 'Lemma3 (ours)'))[:80]))
        p(f'== route2-original minus route2-rerouted: {len(rem)}; by prefix: {split(rem, pnt)}')
        p('   top-level namespaces of the removed names (20 largest): ' + ', '.join(f'{t} {c}' for t, c in Counter(top(n) for n in rem).most_common(20)))
        l3 = S['lemma3-bridge']
        p(f'\n== our Lemma 3 code ({len(l3)}): in route2-rerouted {len(l3 & S["route2-rerouted"])}, '
          f'in route1 {len(l3 & S["route1"])}, in route2-original {len(l3 & S["route2-original"])}')
    return sets


if __name__ == '__main__':
    report(sys.argv[1], sys.argv[2])
