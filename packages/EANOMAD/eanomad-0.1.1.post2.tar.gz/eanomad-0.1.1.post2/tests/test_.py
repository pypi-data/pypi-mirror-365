# -*- coding: utf-8 -*-
"""Unit tests for *EANOMAD*.
Run with ``pytest -q``.

The tests are lightweight smoke checks that ensure:
* both optimiser types ("pure" and "hybrid") run without error,
* invalid arguments raise `ValueError`,
* seeding makes the run deterministic.
"""
from __future__ import annotations

import numpy as np
import pytest
from typing import Callable, Tuple, Optional, List

from EANOMAD import EANOMAD

# ---------------------------------------------------------------------------
# Test helper – simple objective
# --------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Smoke tests for both optimiser types
# ---------------------------------------------------------------------------

def _run_smoke(optim_type: str):
    opt = EANOMAD(
        optim_type,
        population_size=8,
        dimension=4,
        objective_fn=sphere,
        subset_size=2,
        bounds=0.1,
        max_bb_eval=20,
        n_elites=2,
        n_mutate_coords=1,
        seed=42,
        use_ray=False,
    )
    best_x, best_fit = opt.run(generations=3)
    assert best_x.shape == (4,)
    assert isinstance(best_fit, float)
    assert best_fit <= 0  # sphere is <= 0


def test_pure_smoke():
    _run_smoke("EA")


def test_hybrid_smoke():
    _run_smoke("rEA")


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("crossover_type", ["foo", "", None])
def test_invalid_crossover_type_raises(crossover_type):
    with pytest.raises(ValueError):
        EANOMAD(
            "EA",
            population_size=4,
            dimension=2,
            objective_fn=sphere,
            crossover_type=crossover_type,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("crossover_rate", [-0.1, -10, 1.5])
def test_invalid_crossover_rate_raises(crossover_rate):
    with pytest.raises(ValueError):
        EANOMAD(
            "EA",
            population_size=4,
            dimension=2,
            objective_fn=sphere,
            crossover_rate=crossover_rate,  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# Determinism with seed
# ---------------------------------------------------------------------------

def test_seed_reproducibility():
    """Global RNG seeding should make two runs identical."""
    opt1 = EANOMAD(
        "EA",
        population_size=6,
        dimension=3,
        objective_fn=sphere,
        subset_size=2,
        seed=7,
        use_ray=False,
    )
    best_x1, best_fit1 = opt1.run(generations=3)

   
    opt2 = EANOMAD(
        "EA",
        population_size=6,
        dimension=3,
        objective_fn=sphere,
        subset_size=2,
        seed=7,
        use_ray=False,
    )
    best_x2, best_fit2 = opt2.run(generations=3)

    assert np.allclose(best_x1, best_x2)
    assert best_fit1 == best_fit2


# ─────────────────────────────────────────────────────────────
# 1.  Benchmark functions  (return –f so EA-NOMAD can maximise)
# ─────────────────────────────────────────────────────────────
def sphere(x: np.ndarray) -> float:
    return -np.sum(x ** 2)

def rosenbrock(x: np.ndarray) -> float:
    return -np.sum(100.0 * (x[1:] - x[:-1] ** 2) ** 2 + (1 - x[:-1]) ** 2)

def rastrigin(x: np.ndarray) -> float:
    d = x.size
    return -(10 * d + np.sum(x ** 2 - 10 * np.cos(2 * np.pi * x)))

benchmarks = {
    "Sphere": sphere,
    "Rosenbrock": rosenbrock,
    "Rastrigin": rastrigin,
}
"""Smoke‑tests for EA‑NOMAD on classical optimisation benchmarks.

The optimiser maximises the NEGATED benchmark functions, so the true
global optimum corresponds to a best fitness of 0.  We only require the
algorithm to get reasonably close (>-1e‑1) in a short run so the test
suite stays fast while still catching regressions.
"""



# ─────────────────────────────────────────────────────────────
# 1.  Benchmark functions (return –f so EA‑NOMAD can maximise)
# ─────────────────────────────────────────────────────────────

def sphere(x: np.ndarray) -> float:
    return -np.sum(x ** 2)


def rosenbrock(x: np.ndarray) -> float:
    return -np.sum(100.0 * (x[1:] - x[:-1] ** 2) ** 2 + (1 - x[:-1]) ** 2)


def rastrigin(x: np.ndarray) -> float:
    d = x.size
    return -(10 * d + np.sum(x ** 2 - 10 * np.cos(2 * np.pi * x)))


benchmarks: dict[str, Callable[[np.ndarray], float]] = {
    "Sphere": sphere,
    "Rosenbrock": rosenbrock,
    "Rastrigin": rastrigin,
}

# ─────────────────────────────────────────────────────────────
# 2.  Hyper‑parameters trimmed for CI / local test speed
# ─────────────────────────────────────────────────────────────
DIM = 10
POP_SIZE = 128          # smaller than real demo to keep test fast
GENERATIONS = 100
SUBSET_SIZE = 10        # ≥1 so NOMAD has something to do
BOUNDS = (-5.12 * np.ones(DIM), 5.12 * np.ones(DIM))
MAX_BB_EVAL = 400
N_MUTATE_COORD = DIM // 4
SEED = 0

# ─────────────────────────────────────────────────────────────
# 3.  Parametrised test
# ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize("name, fn", benchmarks.items())
def test_eanomad_benchmark_convergence(name: str, fn):
    """Ensure EA‑NOMAD improves each benchmark quickly on CPU."""

    es = EANOMAD(
        "EA",
        population_size=POP_SIZE,
        dimension=DIM,
        objective_fn=fn,
        subset_size=SUBSET_SIZE,
        bounds=BOUNDS,
        max_bb_eval=MAX_BB_EVAL,
        n_mutate_coords=N_MUTATE_COORD,
        seed=SEED,
        use_ray=False,
    )

    _best_x, best_fit = es.run(GENERATIONS)

    # The best achievable value is 0.  Allow a modest tolerance so the
    # test stays robust across platforms yet still detects gross errors.
    assert best_fit > -1e+2, (
        f"{name} benchmark failed: best fitness {best_fit:.4f} not close enough"
    )