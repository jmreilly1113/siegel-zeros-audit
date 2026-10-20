"""Sanity tests for src/effectivity.py: monotonicity in the inputs, the defining identity of delta0, Lemma 12."""
import sys
from fractions import Fraction as Fr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import effectivity as ef  # noqa: E402

Q = 400001
G = Fr(201, 10)
H = 1995262314


def d0(cfg, q0=Q, g=G, H=H):
    return ef.delta0(cfg, q0, g, H)[0]


def test_weaker_theta_lowers_delta0():
    assert d0(ef.Config(theta="RS9")) < d0(ef.Config(theta="PT"))


def test_weaker_cq_lowers_delta0():
    assert d0(ef.Config(c_q="one")) < d0(ef.Config(c_q="half"))


def test_dropping_kappa_lowers_delta0():
    assert d0(ef.Config(use_kappa=False)) < d0(ef.Config(use_kappa=True))


def test_unsourced_mertens_is_weaker_than_rs6():
    assert d0(ef.Config(mertens_H="old")) < d0(ef.Config(mertens_H="RS6"))


def test_larger_q0_raises_delta0():
    assert d0(ef.Config(), q0=10 ** 6) > d0(ef.Config(), q0=Q)


def test_delta0_solves_the_master_inequality():
    # T_up + C_delta * lam_hi * delta0 = 1 (as balls)
    v, p = ef.delta0(ef.Config(), Q, G, H)
    total = p["T"] + ef.E_ / 2 * p["lam_hi"] * v
    assert total.contains(1)


def test_side_conditions_detect_small_gamma():
    sc = dict(ef.side_conditions(Q, Fr(1, 10), H))  # q0^0.1 < H, so N >= H is not guaranteed
    assert sc["SC3 N >= H (log N >= g log q0 > log H)"] is False


def test_lemma12_inequality_all_sigma():
    ok1, ok2, ok3, worst = ef.lemma12_check()
    assert ok1 and ok2 and ok3 and worst > 0


def test_floor_sci_rounds_down():
    from fractions import Fraction as Fr
    v = ef.A(Fr(339929040265590, 10 ** 17))  # 3.3992904026559e-3: nearest-rounding would give ...027
    assert ef.floor_sci(v) == "3.3992904026e-03"
    assert ef.floor_sci(ef.A(Fr(1, 3)), 4) == "3.333e-01"
    assert ef.floor_sci(ef.A(12345), 3) == "1.23e+04"
    assert Fr(ef.floor_sci(v).replace("e", "E")) <= Fr(339929040265590, 10 ** 17)
