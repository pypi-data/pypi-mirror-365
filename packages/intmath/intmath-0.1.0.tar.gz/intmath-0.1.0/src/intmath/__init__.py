from importlib.metadata import version

__version__ = version(__name__)
del version

from math import comb, factorial, gcd, isqrt, lcm, perm

__all__ = ['comb', 'factorial', 'gcd', 'isqrt', 'lcm', 'perm']
