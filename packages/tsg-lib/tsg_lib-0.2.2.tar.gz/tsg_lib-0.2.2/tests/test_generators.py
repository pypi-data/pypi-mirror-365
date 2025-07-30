import pytest
import numpy as np
from tsg.generators import (
    LinearTrendGenerator,
    ConstantGenerator,
    PeriodicTrendGenerator,
    RandomWalkGenerator,
    OrnsteinUhlenbeckGenerator,
    GeometricBrownianMotionGenerator,
    CoxIngersollRossGenerator)

from tsg.modifiers import (
    GaussianNoise,
    PoissonNoise
)

# === LINEAR TREND GENERATOR ===

def test_linear_trend_generator_up():
    """
    Test that LinearTrendGenerator increases by 1 at each step (slope=1).
    """
    gen = LinearTrendGenerator(start_value=100, slope=1)
    values = [gen.generate_value() for _ in range(5)]
    assert values == [101, 102, 103, 104, 105]

def test_linear_trend_generator_down():
    """
    Test that LinearTrendGenerator decreases by 1 at each step (slope=-1).
    """
    gen = LinearTrendGenerator(start_value=100, slope=-1)
    values = [gen.generate_value() for _ in range(5)]
    assert values == [99, 98, 97, 96, 95]

def test_linear_trend_generator_reset_restores_initial_state():
    """
    Ensure LinearTrendGenerator resets correctly to its initial value.
    """
    gen = LinearTrendGenerator(start_value=50, slope=1)
    for _ in range(3): gen.generate_value()
    gen.reset()
    assert gen.generate_value() == 51  # After reset: 50 + 1

# === CONSTANT GENERATOR ===

def test_constant_generator():
    """
    ConstantGenerator always returns the last value passed to it.
    """
    gen = ConstantGenerator()
    val = gen.generate_value(123.45)
    assert val == 123.45
    for _ in range(3):
        assert gen.generate_value(val) == 123.45

# === PERIODIC TREND GENERATOR ===

def test_periodic_trend_generator_repeatable():
    """
    PeriodicTrendGenerator should produce a repeating sine pattern.
    With frequency=π/2, the values should follow [10.0, 11.0, 10.0, 9.0].
    """
    gen = PeriodicTrendGenerator(start_value=10.0, amplitude=1.0, frequency=np.pi / 2)
    values = [gen.generate_value() for _ in range(4)]
    expected = [10.0, 11.0, 10.0, 9.0]  # sin(0), sin(pi/2), sin(pi), sin(3pi/2)
    np.testing.assert_allclose(values, expected, rtol=1e-5)

# === RANDOM WALK GENERATOR ===

def test_random_walk_generator_drift_and_noise():
    """
    RandomWalkGenerator with sigma=0 should act like a pure drift.
    With mu=1.0, values should increase linearly from start_value.
    """
    gen = RandomWalkGenerator(start_value=0.0, mu=1.0, sigma=0.0)
    values = [gen.generate_value() for _ in range(5)]
    expected = [1.0, 2.0, 3.0, 4.0, 5.0]
    np.testing.assert_allclose(values, expected, rtol=1e-5)

def test_random_walk_generator_with_noise_has_variation():
    """
    RandomWalkGenerator with sigma > 0 should show variation in outputs.
    """
    gen = RandomWalkGenerator(start_value=0.0, mu=0.0, sigma=1.0)
    values = [gen.generate_value() for _ in range(10)]
    assert all(isinstance(v, float) for v in values)
    assert len(set(values)) > 1  # Not all values should be identical

# === ORNSTEIN-UHLENBECK GENERATOR ===

def test_ou_generator_mean_reversion():
    """
    OU process with no noise should revert toward its long-term mean (mu).
    Starting below mu should produce an increasing trend.
    """
    gen = OrnsteinUhlenbeckGenerator(mu=10.0, theta=0.5, sigma=0.0, dt=1.0, start_value=0.0)
    values = [gen.generate_value() for _ in range(5)]
    assert all(values[i] < values[i+1] for i in range(len(values)-1))

def test_ou_generator_stochasticity():
    """
    OU process with noise should fluctuate and eventually cross the mean.
    We expect it to go below and/or above the initial value depending on direction.
    """
    gen = OrnsteinUhlenbeckGenerator(mu=0.0, theta=0.3, sigma=1.0, dt=1.0, start_value=5.0)
    values = [gen.generate_value() for _ in range(100)]
    assert any(v < 0.0 for v in values)  # Should cross below mean
    assert len(set(values)) > 1          # Ensure variation


# === GEOMETRIC BROWNIAN MOTION GENERATOR ===


def test_gbm_generator_produces_positive_values():
    """
    GeometricBrownianMotionGenerator should produce strictly positive values.
    """
    gen = GeometricBrownianMotionGenerator(
        start_value=1.0, mu=0.05, sigma=0.1, dt=1.0
    )
    values = [gen.generate_value() for _ in range(100)]
    assert all(v > 0 for v in values)

def test_gbm_generator_with_zero_volatility_behaves_exponentially():
    """
    If sigma = 0, GBM should follow a deterministic exponential growth:
    X_t = X_0 * exp(mu * t)
    """
    mu = 0.05
    dt = 1.0
    X0 = 1.0
    gen = GeometricBrownianMotionGenerator(
        start_value=X0, mu=mu, sigma=0.0, dt=dt
    )
    values = [gen.generate_value() for _ in range(5)]
    expected = [X0 * np.exp(mu * (t+1)) for t in range(5)]
    np.testing.assert_allclose(values, expected, rtol=1e-5)

def test_gbm_generator_reset_works_properly():
    """
    After calling reset(), the GBM generator should restart from start_value.
    """
    gen = GeometricBrownianMotionGenerator(
        start_value=2.0, mu=0.1, sigma=0.1, dt=1.0
    )
    for _ in range(10):
        gen.generate_value()
    gen.reset()
    assert np.isclose(gen.current_value, 2.0)

# === COX-INGERSOLL-ROSS GENERATOR ===

def test_cir_generator_positive_values():
    """
    CIR should stay non-negative when Feller condition is satisfied.
    """
    gen = CoxIngersollRossGenerator(mu=1.0, theta=0.5, sigma=0.5, dt=0.01, start_value=1.0)
    values = [gen.generate_value() for _ in range(1000)]
    assert all(v >= 0.0 for v in values), "CIR went negative despite satisfying Feller condition"

def test_cir_generator_reset():
    """
    After reset, the generator should return to its start value.
    """
    gen = CoxIngersollRossGenerator(mu=1.0, theta=0.5, sigma=0.5, dt=0.01, start_value=1.0)
    for _ in range(50):
        gen.generate_value()
    gen.reset()
    assert gen.current_value == 1.0

def test_cir_feller_condition_violation():
    """
    Ensure that the Cox-Ingersoll-Ross generator enforces the Feller condition.
    The Feller condition requires: 2 * theta * mu >= sigma^2.
    If violated, the constructor should raise a ValueError with explanation.
    """
    mu = 1.0
    theta = 0.1
    sigma = 1.0  # Violates 2 * theta * mu = 0.2 < sigma^2 = 1.0

    with pytest.raises(ValueError, match="Feller condition violated"):
        CoxIngersollRossGenerator(mu=mu, theta=theta, sigma=sigma)


# === GAUSSIAN NOISE MODIFIER ===

def test_gaussian_noise_perturbs_base():
    """
    GaussianNoise should apply perturbations to its base generator.
    We check that output is still float and deviates from base trend.
    """
    base_gen = LinearTrendGenerator(start_value=100, slope=1)
    noisy_gen = GaussianNoise(base_gen, mu=0.0, sigma=1.0)

    noisy_values = [noisy_gen.generate_value(None) for _ in range(5)]
    assert all(isinstance(p, float) for p in noisy_values)

    # Check that noise caused deviation from the clean linear trend
    diffs = [abs(p - (101 + i)) for i, p in enumerate(noisy_values)]
    assert any(diff > 0 for diff in diffs)


# === POISSON NOISE MODIFIER ===


def test_poisson_noise_modifier_adds_random_jumps():
    """
    PoissonNoiseModifier should perturb the output of the base generator
    by adding Poisson-distributed noise at every time step.

    We test that:
    - Values remain floats.
    - The output deviates from the clean linear trend.
    """
    base = LinearTrendGenerator(start_value=100.0, slope=1.0)
    mod = PoissonNoise(generator=base, lam=2.0, direction="both")

    values = [mod.generate_value(None) for _ in range(10)]

    assert all(isinstance(v, float) for v in values)

    expected = [101 + i for i in range(10)]
    diffs = [abs(v - e) for v, e in zip(values, expected)]
    assert any(d > 0.0 for d in diffs)  # noise must cause at least one deviation


