"""
Diabicus: A calculator that plays music, lights up, and displays facts.
Copyright (C) 2016 Michael Lipschultz

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import math
import os
from functools import reduce

from .compute import ComputationError

def is_int(val):
    return isinstance(val, int) or (isinstance(val, float) and val % 1 == 0)

def is_rational(val):
    return isinstance(val, (int, float)) and not is_irrational(val)

def is_irrational(val):
    return is_transcendental(val) or val in {2**.5, GOLDEN_RATIO}

def is_transcendental(val):
    return val in (math.pi, math.e)

def is_real(val):
    return isinstance(val, (int, float))

def is_complex(val):
    return isinstance(val, complex)

def is_surreal(val):
    return False

def is_number(val):
    return isinstance(val, (int, float, complex))

def is_error(val):
    return isinstance(val, ComputationError)

GOLDEN_RATIO = (1 + 5**0.5) / 2
GRAHAMS_NUMBER = False
I = complex(0, 1)

PI_DIGITS = (3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4, 6, 2,
             6, 4, 3, 3, 8, 3, 2, 7, 9, 5, 0, 2, 8, 8, 4, 1, 9, 7, 1, 6, 9, 3,
             9, 9, 3, 7, 5, 1, 0, 5, 8, 2, 0, 9, 7, 4, 9, 4, 4, 5, 9, 2, 3, 0,
             7, 8, 1, 6, 4, 0, 6, 2, 8, 6, 2, 0, 8, 9, 9, 8, 6, 2, 8, 0, 3, 4,
             8, 2, 5, 3, 4, 2, 1, 1, 7, 0, 6, 7, 9, 8, 2, 1, 4
            )

PRIME_NUMBERS = []
def __load_primes():
    global PRIME_NUMBERS
    path, name = os.path.split(__file__)
    with open(os.path.join(path, 'prime_numbers.csv')) as fin:
        PRIME_NUMBERS = [int(v) for v in fin.read().split(', ')]
__load_primes()

def is_prime(number):
    return is_int(number) and number > 1 and number in PRIME_NUMBERS

FACTORS_ALL = 'all'
FACTORS_PROPER = 'proper'
FACTORS_PRIME = 'prime'
def factors(n, form=FACTORS_PROPER):
    if form == FACTORS_PRIME:
        primes = []
        i = 2
        while n % i == 0:
            primes.append(i)
            n /= i
        i = 3
        while n > 1:
            while n % i == 0:
                primes.append(i)
                n /= i
            i += 2
        return primes
    else:
        all_factors = reduce(list.__add__, ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0))
        if form == FACTORS_PROPER:
            all_factors.remove(n)
        return all_factors


FIBONACCI_NUMBERS = (0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377,
                     610, 987, 1597, 2584, 4181, 6765
                    )
LUCAS_NUMBERS = (2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322, 521, 843,
                 1364, 2207, 3571, 5778, 9349, 15127, 24476, 39603, 64079,
                 103682, 167761, 271443, 439204, 710647, 1149851, 1860498,
                 3010349, 4870847, 7881196, 12752043, 20633239, 33385282
                )
def is_subsequence_of(needle, haystack):
    for offset in (i for i, x in enumerate(haystack) if x == needle[0]):
        if offset + len(needle) > len(haystack):
            return False

        matches = [needle[i] == haystack[offset+i] for i in range(1, len(needle))]

        if len(matches) == len(needle)-1 and all(matches):
            return True

    return False

def is_close(num1, num2, threshold=1e-5, method='raw'):
    if isinstance(num1, ComputationError) or isinstance(num2, ComputationError):
        return False
    elif hasattr(num1, '__iter__'):
        return any(is_close(n, num2, threshold) for n in num1)
    elif hasattr(num2, '__iter__'):
        return any(is_close(num1, n, threshold) for n in num2)
    elif (isinstance(num1, complex) or isinstance(num2, complex)) and type(num1) != type(num2):
        return False
    else:
        if method == 'pct':
            return abs(num1-num2) / max(num1, num2) < threshold
        else:
            return abs(num1-num2) < threshold
