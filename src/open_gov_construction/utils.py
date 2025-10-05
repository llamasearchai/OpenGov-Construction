from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

import numpy as np

@dataclass(frozen=True)
class RandomConfig:
    seed: int = 42

    def rng(self) -> np.random.Generator:
        return np.random.default_rng(self.seed)

