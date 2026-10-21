import os
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import effectivity as ef  # noqa: E402
import effectivity_banks_device as dv  # noqa: E402
import flint  # noqa: E402

PARAMS = {400001: (Fr(201, 10), 1995262314), 10 ** 10 + 1: (Fr(153, 10), 2818382931)}
NEW = {400001: (Fr(103, 5), 1995262314, Fr(31, 20)), 10 ** 10 + 1: (Fr(77, 5), 2660725059, Fr(29, 20))}


def setup_module():
    flint.ctx.prec = 256


def test_new_bound_at_least_old_bound():
    for q0, (g, H, s) in NEW.items():
        new, _ = dv.delta0(q0, g, H, s)
        old, _ = ef.delta0(ef.Config(c_q="old"), q0, *PARAMS[q0])
        assert new > old


def test_device_alone_beats_every_c_q_at_same_parameters():
    for q0, (g, H) in PARAMS.items():
        dev, _ = dv.delta0(q0, g, H, Fr(1))
        for cq in ("old", "half", "one"):
            old, _ = ef.delta0(ef.Config(c_q=cq), q0, g, H)
            assert dev > old


def test_shift_one_with_c_q_half_reproduces_effectivity():
    # with s = 1 and c_dev = 1/2 the new formula is derivation.md's with c_q = 1/2
    for q0, (g, H) in PARAMS.items():
        a, _ = dv.delta0(q0, g, H, Fr(1), c_dev=Fr(1, 2))
        b, _ = ef.delta0(ef.Config(c_q="half"), q0, g, H)
        assert a.overlaps(b)


def test_weakening_the_device_constant_lowers_delta0():
    for q0, (g, H, s) in NEW.items():
        base, _ = dv.delta0(q0, g, H, s)
        weaker, _ = dv.delta0(q0, g, H, s, c_dev=Fr(1, 2 * H) + Fr(1, 10))
        stronger, _ = dv.delta0(q0, g, H, s, c_dev=Fr(0))
        assert weaker < base < stronger


def test_side_conditions_hold():
    for q0, (g, H, s) in NEW.items():
        assert all(ok for _, ok in dv.side_conditions(q0, g, H, s))


def test_shift_out_of_range_rejected():
    try:
        dv.delta0(400001, Fr(201, 10), 1995262314, Fr(21, 10))
    except AssertionError:
        return
    raise AssertionError("shift > 2 accepted")
