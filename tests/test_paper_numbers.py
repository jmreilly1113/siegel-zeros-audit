import os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import paper_numbers

ROOT = os.path.join(os.path.dirname(__file__), '..')


def test_counts_and_cross_checks():
    v = {k: d['value'] for k, d in paper_numbers.compute(ROOT).items()}
    assert v['NRefConfigs'] == v['NLeanAccept'] == 189
    assert v['NNanodaPinnedAccept'] + v['NCrashNine'] == 189
    assert v['NInIssueFiftyFive'] == 7


def test_every_number_has_an_existing_source():
    for k, d in paper_numbers.compute(ROOT).items():
        assert os.path.isfile(os.path.join(ROOT, d['source'])), k


def test_tex_macros_are_valid():
    t = paper_numbers.tex(paper_numbers.compute(ROOT))
    names = re.findall(r'\\newcommand\{\\([^}]*)\}', t)
    assert names and all(re.fullmatch(r'[A-Za-z]+', n) for n in names)
    assert len(names) == len(set(names))
