from __future__ import annotations

import numpy as np

from open_gov_construction.utils import RandomConfig

def test_random_config_default_seed() -> None:
    config = RandomConfig()
    assert config.seed == 42
    rng = config.rng()
    assert isinstance(rng, np.random.Generator)

def test_random_config_custom_seed() -> None:
    config = RandomConfig(seed=123)
    assert config.seed == 123
    rng1 = config.rng()
    rng2 = config.rng()
    # Same seed should produce same sequence
    val1 = rng1.random()
    val2 = rng2.random()
    assert val1 == val2

def test_random_config_deterministic() -> None:
    config = RandomConfig(seed=999)
    rng = config.rng()
    samples = [rng.random() for _ in range(5)]
    # Reset with same seed
    rng2 = config.rng()
    samples2 = [rng2.random() for _ in range(5)]
    assert samples == samples2


