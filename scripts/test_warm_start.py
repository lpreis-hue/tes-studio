"""Verify that grid simulations reuse only compatible neighbouring results."""

from __future__ import annotations

import sys
import types
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class FakeGibbs:
    calls = []

    def __init__(self, *args, **kwargs):
        pass

    def solve_gibbs(self, initial, T, P, initial_guess=None):
        guess = None if initial_guess is None else np.asarray(initial_guess).copy()
        self.calls.append((np.asarray(initial).copy(), guess))
        return list(np.asarray(initial, dtype=float) + len(self.calls))


class FakeEntropy:
    calls = []

    def __init__(self, *args, **kwargs):
        pass

    def solve_entropy(self, initial, T, P, initial_guess=None,
                      temperature_guess=None):
        guess = None if initial_guess is None else np.asarray(initial_guess).copy()
        self.calls.append((np.asarray(initial).copy(), guess, temperature_guess))
        call_number = len(self.calls)
        return list(np.asarray(initial, dtype=float) + call_number), 500.0 + call_number


gibbs_module = types.ModuleType("app.gibbs")
gibbs_module.Gibbs = FakeGibbs
sys.modules["app.gibbs"] = gibbs_module

entropy_module = types.ModuleType("app.entropy")
entropy_module.Entropy = FakeEntropy
sys.modules["app.entropy"] = entropy_module

from app.auxiliar_func.run_entropy import RunEntropy
from app.auxiliar_func.run_gibbs import RunGibbs


common = dict(
    data={},
    species=np.array([]),
    initial=np.array([1.0, 2.0]),
    components=np.array(["A", "B"]),
    Tmin=300.0,
    Tmax=400.0,
    Pmin=1.0,
    Pmax=2.0,
    nT=1,
    nP=2,
    reference_componente="A",
    reference_componente_min=1.0,
    reference_componente_max=2.0,
    n_reference_componente=2,
)

RunGibbs(**common).run_gibbs()
assert FakeGibbs.calls[0][1] is None
assert FakeGibbs.calls[1][1] is None
np.testing.assert_allclose(FakeGibbs.calls[2][1], [2.0, 3.0])
np.testing.assert_allclose(FakeGibbs.calls[3][1], [4.0, 4.0])

RunEntropy(**common).run_entropy()
assert FakeEntropy.calls[0][1] is None
assert FakeEntropy.calls[1][1] is None
np.testing.assert_allclose(FakeEntropy.calls[2][1], [2.0, 3.0])
np.testing.assert_allclose(FakeEntropy.calls[3][1], [4.0, 4.0])
assert FakeEntropy.calls[2][2] == 501.0
assert FakeEntropy.calls[3][2] == 502.0

print("Reaproveitamento seguro de soluções verificado.")
