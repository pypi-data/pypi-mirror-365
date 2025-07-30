# =============================
# utils.py — Utility Functions
# =============================

import numpy as np
import random
import os

def set_random_seed(seed: int = 42):
    """
    Set global random seed for reproducibility.

    Parameters:
        seed (int): The random seed to use. Default is 42.

    Applies to:
        - numpy
        - random
        - os.environ['PYTHONHASHSEED']
    """
    np.random.seed(seed)
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
