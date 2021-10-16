# Copyright (c) 2021 Oleg Polakow. All rights reserved.
# This code is licensed under Apache 2.0 with Commons Clause license (see LICENSE.md for details)

"""Utilities for random number generation."""

import random
import numpy as np

from vectorbt.nb_registry import register_jit


@register_jit(cache=True)
def set_seed_nb(seed: int) -> None:
    """Set seed in numba."""
    np.random.seed(seed)


def set_seed(seed: int) -> None:
    """Set seed."""
    random.seed(seed)
    np.random.seed(seed)
    set_seed_nb(seed)
