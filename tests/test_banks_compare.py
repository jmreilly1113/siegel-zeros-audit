import os
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import banks_compare as bc  # noqa: E402
import effectivity as ef  # noqa: E402
from flint import arb  # noqa: E402


def test_banks_closed_form():
    ok, d0 = bc.part_a()
    assert ok
    assert d0.overlaps(81 / (5888 * (arb(3) / 2).exp()))
    assert bc.floor_sci(d0) == "3.0695555319e-03"


def test_generalized_reproduces_effectivity():
    for q0, g, H in [(400001, Fr(201, 10), 1995262314), (10 ** 10 + 1, Fr(153, 10), 2818382931)]:
        a, _ = bc.delta0(bc.OURS, q0, g, H)
        b, _ = ef.delta0(ef.Config(c_q="old"), q0, g, H)
        assert a.overlaps(b)


def test_banks_step3_exact_beats_closed_form():
    # solving his Step 3 inequality exactly can only improve on his rounded 3/32 split
    d, _ = bc.delta0(bc.BANKS, 10 ** 10, Fr(22), bc.H_PAPER)
    _, d0 = bc.part_a()
    assert d > d0


def test_banks_s1_mode_needs_large_H():
    try:
        bc.delta0(bc.BANKS, 10 ** 10, Fr(22), 10 ** 6)
    except AssertionError:
        return
    raise AssertionError("S1 >= N^4 M used with H < 8*97^3")
