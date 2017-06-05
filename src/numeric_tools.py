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
import re
from functools import reduce

from .compute import ComputationError

def is_int(val):
    """ Returns True if val is an int or a float with 0 fractional part """
    return isinstance(val, int) or (isinstance(val, float) and val % 1 == 0)

def is_rational(val):
    """
    Returns True if val is an int or float and not irrational.

    Determining irrationality is done through the is_irrational method.
    """
    return isinstance(val, (int, float)) and not is_irrational(val)

def is_irrational(val):
    """
    Returns True if val is irrational.

    Irrationality is determined by whether val is transcendental (as
    determined by is_transcendental) or sqrt(2) or golden ratio.
    """
    return is_transcendental(val) or val in {2**.5, GOLDEN_RATIO}

def is_transcendental(val):
    """ Returns True if val is transcendental (i.e. pi or e). """
    return val in (math.pi, math.e)

def is_real(val):
    """ Returns True if val is int or float. """
    return isinstance(val, (int, float))

def is_complex(val):
    """ Returns True if val is complex. """
    return isinstance(val, complex)

def is_surreal(val):
    """ Returns True if val is surreal (currently always returns False). """
    return False

def is_number(val):
    """ Returns True if val is int, float, or complex. """
    return isinstance(val, (int, float, complex))

def is_error(val):
    """ Returns True if val is a ComputationError. """
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
    """
    Loads a comma-delimited list of prime numbers into PRIME_NUMBERS.

    Prime numbers are loaded from the file prime_numbers.csv in the same
    location as this python file and stores them into the global
    variable PRIME_NUMBERS.
    """
    global PRIME_NUMBERS
    path = os.path.dirname(__file__)
    with open(os.path.join(path, 'prime_numbers.csv')) as fin:
        PRIME_NUMBERS = [int(v) for v in fin.read().split(',')]
__load_primes()

def is_prime(number):
    """ Returns True if number is a prime number. """
    return is_int(number) and number > 1 and int(number) in PRIME_NUMBERS

FACTORS_ALL = 'all'
FACTORS_PROPER = 'proper'
FACTORS_PRIME = 'prime'
def factors(num, form=FACTORS_PROPER):
    """
    Return a list of factors for the provided number.

    If form is FACTORS_PRIME, then the list will only contain the prime
    factors of num.  The product of the values in the list will always
    return num.  That is, if the number is a product of more than one of
    the same prime (e.g. 12 = 2*2*3), then the list will contain those
    duplicates (e.g. [2, 2, 3] in the example).

    If form is FACTORS_ALL, then the list will contain all positive
    integers that exactly divide num.  For example, with num=12, the
    list returned is [1, 2, 3, 4, 12].

    If form is FACTORS_PROPER (default), then the list will be the same
    as FACTORS_ALL, except the list will not include num.  So, for
    num=12, the list returned would be [1, 2, 3, 4].

    If num is not an integer (as determined by is_int) greater than 1,
    return empty list.
    """
    if not is_int(num) or num < 2:
        return []
    if form == FACTORS_PRIME:
        primes = []
        i = 2
        while num % i == 0:
            primes.append(i)
            num /= i
        i = 3
        while num > 1:
            while num % i == 0:
                primes.append(i)
                num /= i
            i += 2
        return primes
    else:
        all_factors = reduce(list.__add__,
                             ([i, num//i] for i in range(1, int(num**0.5) + 1) if num % i == 0)
                            )
        if form == FACTORS_PROPER:
            all_factors.remove(num)
        return all_factors


FIBONACCI_NUMBERS = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233,
                     377, 610, 987, 1597, 2584, 4181, 6765, 10946, 17711,
                     28657, 46368, 75025, 121393, 196418, 317811, 514229,
                     832040, 1346269
                     ]
LUCAS_NUMBERS = (2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322, 521, 843,
                 1364, 2207, 3571, 5778, 9349, 15127, 24476, 39603, 64079,
                 103682, 167761, 271443, 439204, 710647, 1149851, 1860498,
                 3010349, 4870847, 7881196, 12752043, 20633239, 33385282
                )
def is_subsequence_of(needle, haystack):
    """
    Returns True if needle occurs as a consecutive subsequence in haystack.

    Both needle and haystack must be ordered containers.  The values in
    needle must appear in haystack in the order they appear in needle
    and must be consecutive in haystack.

    For example, with needle=[1,2,3] and haystack=[1,1,2,3,4], the
    function returns True since needle starts at index 1 in haystack.

    With needle=[1,2,4] and haystack=[1,1,2,3,4], the function returns
    False since, although the values do appear in haystack in the
    correct order, they are not consecutive.

    An empty needle will always return False.
    """
    if len(needle) == 0:
        return False
    for offset in (i for i, x in enumerate(haystack) if x == needle[0]):
        if offset + len(needle) > len(haystack):
            return False

        matches = [needle[i] == haystack[offset+i] for i in range(1, len(needle))]

        if len(matches) == len(needle)-1 and all(matches):
            return True

    return False

def is_close(num1, num2, threshold=1e-5, method='raw'):
    """
    Returns True if num1 is within threshold of num2.

    If method is 'raw', then the closeness is determined by the absolute
    value of the difference between num1 and num2.

    If method is 'pct', then the absolute value of percent difference is
    calculated and used.

    num1 and num2 can be iterable.  If one is iterable, then as long as
    one value in the iterable object is close to the other number, the
    function returns True.  If both are iterable, then as long as one
    value in num1 is close to one value in num2, the function returns
    True.
    """
    if isinstance(num1, ComputationError) or isinstance(num2, ComputationError):
        return False
    elif hasattr(num1, '__iter__'):
        return any(is_close(n, num2, threshold) for n in num1)
    elif hasattr(num2, '__iter__'):
        return any(is_close(num1, n, threshold) for n in num2)
    elif ((isinstance(num1, complex) or isinstance(num2, complex))
          and not isinstance(num1, type(num2))):
        return False
    else:
        if method == 'pct':
            if num1 == num2 and num1 == 0:
                return True
            else:
                return abs(num1-num2) / max([abs(v) for v in (num1, num2) if v != 0]) < threshold
        else:
            return abs(num1-num2) < threshold
