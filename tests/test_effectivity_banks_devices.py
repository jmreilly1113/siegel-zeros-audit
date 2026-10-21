import math
import os
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import effectivity_banks_devices as dv  # noqa: E402
import flint  # noqa: E402

Q_LZZ = 10 ** 10 + 1


def setup_module():
    flint.ctx.prec = 256


def file_float_delta0(q0, gam, H, cq, s=1.0, banks_device=False):
    """Transcription of the reference function in refs/improved-constants-from-banks-devices.txt (lines 115-130);
    the file itself is not executed."""
    kappa = 0.5 * (2 - 0.5772156649015329 - 2 * math.log(2)) - 0.5 * math.log(math.pi)
    l = math.log(q0)
    lam_lo = 4 * gam / 3
    lam_hi = lam_lo + 4 / 3 * math.log(1 + q0 ** (-gam)) / l
    L = lam_lo * l
    U = math.exp(min(L, 700))
    rho = 768 * 97 ** 2 / H
    Cl = math.exp(s) / 4 + (1 / (2 * H) if banks_device else cq)
    CH = math.log(H) + 1 / (2 * math.log(H)) + 1 / (2 * L) + math.exp(s) / 2 * kappa
    A = (0.75 * (1 + rho) + (Cl + 0.5 * (1 + rho)) / lam_lo + (CH + (1 + rho) * math.log(8)) / L
         + (1 + 7.5e-7) * 4 * 97 ** 2 / (H ** (2 / 3) * L) + 6 * 97 ** 2 / (H ** (2 / 3) * U))
    return (1 - A) / (math.exp(s) / (2 * s * s) * lam_hi)


# the file's table (lines 97-101): (gamma, H, s, banks_device, printed value)
FILE_ROWS = [(Fr(153, 10), 2818382931, Fr(1), False, 4.4674e-3),
             (Fr(179, 10), 3162277660, Fr(3, 2), False, 5.2308e-3),
             (Fr(132, 10), 2238721139, Fr(1), True, 5.1811e-3),
             (Fr(158, 10), 2818382931, Fr(3, 2), True, 5.9298e-3)]


def test_s1_no_device_reproduces_note_v2():
    for q0, (cq, g, H, v2) in dv.NOTE_V2.items():
        d, _ = dv.delta0(q0, g, H, Fr(1), device=False, cq=cq)
        assert dv.floor_sci(d) == v2


def test_each_device_alone_moves_delta0_up():
    for q0, (cq, g, H, _) in dv.NOTE_V2.items():
        base, _ = dv.delta0(q0, g, H, Fr(1), device=False, cq=cq)
        dev2, _ = dv.delta0(q0, g, H, Fr(1), device=True)
        assert dev2 > base                                  # primes-dividing-q device, same (gamma, H)
    # shift device, at the file's parameters for "s = 3/2 only" vs note-v2 (LZZ row)
    base, _ = dv.delta0(Q_LZZ, Fr(153, 10), 2818382931, Fr(1), device=False)
    dev1, _ = dv.delta0(Q_LZZ, Fr(179, 10), 3162277660, Fr(3, 2), device=False)
    assert dev1 > base


def test_matches_file_floats_within_1e_6_relative():
    cq = math.log(2) / (2 * math.log(1e10 + 1)) + 1 / 3
    for g, H, s, dev, printed in FILE_ROWS:
        ours, _ = dv.delta0(Q_LZZ, g, H, s, device=dev)
        f = file_float_delta0(1e10 + 1, float(g), H, cq, float(s), dev)
        assert abs(float(ours.mid()) / f - 1) < 1e-6
        assert abs(float(ours.mid()) - printed) <= 0.5e-7 + 1e-12   # printed to 5 significant digits


def test_side_conditions_of_certified_rows():
    for q0, g, H, s in [(Q_LZZ, Fr(63, 4), 2754228703, Fr(3, 2)), (Q_LZZ, Fr(767, 50), 2691534804, Fr(287, 200)),
                        (400001, Fr(2033, 100), 1995262314, Fr(3, 2)), (400001, Fr(41, 2), 1995262314, Fr(61, 40)),
                        (3, Fr(131), 1083926914, Fr(3, 2)), (3, Fr(6547, 50), 1083926914, Fr(2))]:
        assert all(ok for _, ok in dv.side_conditions(q0, g, H, s))
