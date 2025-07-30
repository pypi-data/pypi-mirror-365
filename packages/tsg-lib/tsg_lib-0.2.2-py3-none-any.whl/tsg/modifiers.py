from .generators import BaseGenerator
import numpy as np

# === Wrappers ===
class GaussianNoise(BaseGenerator):
    def __init__(self, generator, mu=0.0, sigma=0.2):
        """
        Wraps any generator and adds Gaussian noise to its output.
        """
        self.generator = generator
        self.mu = mu
        self.sigma = sigma

    def generate_value(self, last_value):
        base_value = self.generator.generate_value(last_value)
        noise = np.random.normal(self.mu, self.sigma)
        return base_value + noise

    def reset(self):
        self.generator.reset()


class PoissonNoise(BaseGenerator):
    def __init__(self, generator, lam=1.0, direction='positive'):
        """
        Adds Poisson-distributed noise at each time step.

        Parameters:
        - generator: the base generator to wrap
        - lam: lambda parameter of the Poisson distribution (controls intensity)
        - direction: 'positive', 'negative', or 'both' (default 'positive')
        """
        assert direction in {'positive', 'negative', 'both'}, "Invalid direction"
        self.generator = generator
        self.lam = lam
        self.direction = direction

    def generate_value(self, last_value):
        base = self.generator.generate_value(last_value)
        jump = np.random.poisson(self.lam)

        if self.direction == 'positive':
            return base + jump
        elif self.direction == 'negative':
            return base - jump
        elif self.direction == 'both':
            sign = np.random.choice([-1, 1])
            return base + sign * jump

    def reset(self):
        self.generator.reset()
