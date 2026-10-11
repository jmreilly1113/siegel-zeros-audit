"""Set logic of src/route_overlap.py on a small hand-made example."""
from fractions import Fraction
import gzip
import io
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import route_overlap as ro  # noqa: E402


def test_pair_stats():
    a = {'Nat.add_comm', 'Real.pi', 'OAI.X.foo', 'Lemma3.bar'}
    b = {'Nat.add_comm', 'Real.pi', 'Complex.exp', 'OAI.X.baz'}
    s = ro.pair_stats(a, b)
    assert (s['A'], s['B'], s['A&B'], s['A|B'], s['A-B'], s['B-A']) == (4, 4, 2, 6, 2, 2)
    assert s['jaccard'] == Fraction(2, 6)
    assert ro.pair_stats(set(), set())['jaccard'] == 0


def test_auto_and_category():
    assert ro.is_auto('Foo.bar._proof_1')
    assert ro.is_auto('Foo.match_2')
    assert ro.is_auto('List.rec')
    assert ro.is_auto('Foo.eq_1') and ro.is_auto('Foo.below') and ro.is_auto('_private.X.0.y')
    assert not ro.is_auto('Real.pi') and not ro.is_auto('Nat.recDiag') and not ro.is_auto('Foo.induction_on')
    pnt = {'Complex.Hadamard.foo'}
    assert ro.category('OAI.SiegelZeros.x', pnt) == 'OAI'
    assert ro.category('Lemma3.interpolation', pnt) == 'Lemma3 (ours)'
    assert ro.category('Complex.Hadamard.foo', pnt) == 'PNT patch'
    assert ro.category('Nat.succ', pnt) == 'core'
    assert ro.category('Batteries.x', pnt) == 'Batteries'
    assert ro.category('Real.pi', pnt) == 'Mathlib-style'
    assert ro.category('id', pnt) == 'root (no namespace)'
    assert ro.private_module('_private.Mathlib.Data.Nat.Basic.0.Nat.foo') == 'Mathlib.Data.Nat.Basic'
    assert ro.category('_private.Mathlib.Data.Nat.Basic.0.Nat.foo', pnt) == 'Mathlib-style'
    assert ro.category('_private.OAI.NumberTheory.X.0.OAI.y', pnt) == 'OAI'
    assert ro.category('_private.Init.Data.List.0.List.z', pnt) == 'core'
    assert ro.category('_private.OAI.NumberTheory.SiegelZeros.PaperLemma3.Lemma3.0.Lemma3.w', pnt) == 'Lemma3 (ours)'
    sp = ro.split({'Real.pi', 'Nat.succ', 'id', 'OAI.a'}, pnt)
    assert sp['Mathlib-style'] == 1 and sp['core'] == 1 and sp['root (no namespace)'] == 1 and sp['OAI'] == 1
    assert sum(sp.values()) == 4


def test_report_end_to_end(tmp_path):
    lists = {
        'route1': ['Real.pi', 'Nat.succ', 'OAI.A.r1', 'Shared.x'],
        'route2-original': ['Real.pi', 'Nat.succ', 'OAI.B.r2', 'OAI.B.cor4', 'Complex.Hadamard.foo'],
        'route2-rerouted': ['Real.pi', 'Nat.succ', 'OAI.B.r2', 'Lemma3.interpolation', 'Complex.Hadamard.foo'],
        'mainrerouted-challenge': ['Real.pi'],
        'lemma3-bridge': ['Lemma3.interpolation', 'Real.pi'],
    }
    for k, v in lists.items():
        for conv in ('full', 'referenced'):
            with gzip.open(tmp_path / f'{k}.{conv}.txt.gz', 'wt', encoding='utf-8') as f:
                f.write('\n'.join(v) + '\n')
    pnt = tmp_path / 'pnt.txt.gz'
    with gzip.open(pnt, 'wt', encoding='utf-8') as f:
        f.write('Complex.Hadamard.foo\n')
    out = io.StringIO()
    sets = ro.report(str(tmp_path), str(pnt), out)
    r = sets['referenced']
    assert r['route1'] & r['route2-original'] == {'Real.pi', 'Nat.succ'}
    assert r['route2-rerouted'] - r['route2-original'] == {'Lemma3.interpolation'}
    assert r['route2-original'] - r['route2-rerouted'] == {'OAI.B.cor4'}
    text = out.getvalue()
    assert 'route1 & route2-original: 0' in text
    assert 'route1           route2-original         4        5        2        7' in text
