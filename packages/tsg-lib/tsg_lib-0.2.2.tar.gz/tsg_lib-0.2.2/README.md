# tsg – Modular Time Series Generator Library

**tsg** is a lightweight Python library for generating synthetic time series data using modular and composable generators.  
It is designed for research, simulation, and testing of sequential decision-making algorithms, especially in finance and machine learning.

---

## 🚀 Features

- 📈 Core generators: linear trend, periodic trend, constant value
- 🎲 Noise wrappers: add Gaussian noise or build your own modifiers
- 🔁 Stateful generators with `reset()` support
- 🧱 Easy to extend with your own generator or modifier classes

---

## 📦 Installation


Install through GitHub from any location:

```bash
pip install git+https://github.com/MSCA-DN-Digital-Finance/tsg.git
```

Install through PyPi from any location:

```bash
pip install tsg-lib
```


## 🛠️ Example Usage

Here’s how to generate a noisy linear trend time series using `tsg`:

```python
from tsg.generators import LinearTrendGenerator
from tsg.modifiers import GaussianNoise

# Create a linear trend generator (increasing by +1 each step)
linear_generator = LinearTrendGenerator(start_value=100, slope=1)

# Wrap it with Gaussian noise (mean=0, std=1)
noisy_generator = GaussianNoise(linear_generator, mu=0.0, sigma=1.0)

# Generate a few data points
values = []
for _ in range(10):
    value = noisy_generator.generate_value(None)
    values.append(value)

print(values)
```

## 🧠 API Overview

### Core Generators (`tsg.generators`)

| Class                         | Description                                                             | Parameters                                 |
|------------------------------|-------------------------------------------------------------------------|--------------------------------------------|
| `LinearTrendGenerator`       | Linearly increases or decreases the value at each step                  | `start_value`, `slope`                     |
| `ConstantGenerator`          | Returns a fixed value (e.g., simulates cash)                            | None (uses `last_value` in `generate_value`) |
| `PeriodicTrendGenerator`     | Generates a sinusoidal time series with set amplitude and frequency     | `start_value`, `amplitude`, `frequency`    |
| `RandomWalkGenerator`        | Simulates Brownian motion: a drifting random walk with optional noise   | `start_value`, `mu`, `sigma`               |
| `OrnsteinUhlenbeckGenerator` | Simulates mean-reverting noise with drift toward a long-term mean       | `mu`, `theta`, `sigma`, `dt`, `start_value`|
| `CoxIngersollRossGenerator`  | Square-root mean-reverting process with non-negativity and Feller condition         | `mu`, `theta`, `sigma`, `dt`, `start_value`|
| `GeometricBrownianMotionGenerator` | Simulates geometric Brownian motion for stock-like multiplicative noise | `start_value`, `mu`, `sigma`, `dt`        |



### Modifier Wrappers (`tsg.modifiers`)

| Class                         | Description                                                                 | Parameters                              |
|-------------------------------|-----------------------------------------------------------------------------|------------------------------------------|
| `GaussianNoise`               | Adds Gaussian noise (`N(mu, sigma)`) to any base generator                 | `mu`, `sigma`                            |
| `PoissonNoiseModifier`        | Adds Poisson-distributed noise to each step                                | `lam`, `direction`                       |


### Notes

- `direction` can be `'positive'`, `'negative'`, or `'both'` for both jump modifiers.
- `PoissonNoiseModifier` samples a new Poisson value at **every step**.
- `CompoundPoissonJumpModifier` samples **N ∼ Poisson(λ)** at reset and applies exactly N jumps randomly across T steps.
- All modifiers are compatible with any `BaseGenerator`.

### Meta-Generators (`tsg.meta_generators`)

| Class                   | Description                                                                 | Parameters                                                |
|-------------------------|-----------------------------------------------------------------------------|-----------------------------------------------------------|
| `RegimeSwitchGenerator` | Switches between generators at predefined time steps                        | `generator_classes`, `generator_params_list`, `switch_times` |
| `MarkovSwitchGenerator` | Switches between generators using a Markov transition matrix                | `generator_classes`, `generator_params_list`, `transition_matrix`, `initial_state` |



All components implement the `BaseGenerator` interface with:

- `generate_value(last_value)` – returns the next value in the sequence
- `reset()` – resets any internal state (optional for stateless generators)


---

## Acknowledgments

Funded by the European Union. Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or European Research Executive Agency (REA). Neither the European Union nor the granting authority can be held responsible for them.

![EU Logo](images/eu_funded_logo.jpg)

## License

MIT — see LICENSE.