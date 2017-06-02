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

import sys
import decimal
import math

from . import numeric_tools

DEFAULT_NONZERO_THRESHOLD = 1e-15

def simplify_complex(value, real_nonzero_threshold=DEFAULT_NONZERO_THRESHOLD, imag_nonzero_threshold=None):
    """
    Convert close-to-zero parts of complex value to zero.

    If imag_nonzero_threshold is None, then it defaults to the value of
    real_nonzero_threshold.

    If both value.real and value.imag are close to zero, then int(0) is
    returned.
    """
    if imag_nonzero_threshold is None:
        imag_nonzero_threshold = real_nonzero_threshold

    real = value.real if abs(value.real) >= real_nonzero_threshold else 0

    if abs(value.imag) < imag_nonzero_threshold:
        return real
    else:
        return complex(real, value.imag)

def pretty_print_complex(value,
                         real_tostr_fn=lambda val: (str(val) if not numeric_tools.is_int(val)
                                                    else str(int(val))),
                         imag_tostr_fn=None, imaginary_indicator='i', display_0=False
                        ):
    """
    Convert complex number value to displayable string.

    real_tostr_fn is a function taking a number and returning a string
    representation.  Defaults to str.

    If imag_tostr_fn is None (default, then use the same function
    specified by real_tostr_fn.
    """
    if imag_tostr_fn is None:
        imag_tostr_fn = real_tostr_fn

    real = real_tostr_fn(value.real)
    imag = imag_tostr_fn(value.imag)

    if display_0 or (value.imag != 0 and value.real != 0):
        return '%s + %s%s' % (real, imag, imaginary_indicator)
    elif value.imag == 0:
        return real
    else:
        return imag + imaginary_indicator

def to_pretty_x10(num, dec_places=5, prepend='', append='', max_int_length=10):
    """ Format num to look like nnn×10^mmm. """
    if num < sys.float_info.min or num > sys.float_info.max:
        val = decimal.Decimal(num)
        decimal.getcontext().prec = dec_places+1
        val = str(val.normalize())
    elif not numeric_tools.is_int(num) or math.log10(num) > max_int_length:
        val = ('%0.'+str(dec_places+1)+'G') % num
        significand_exponent = val.split('E')
        if len(significand_exponent) == 1:
            left = significand_exponent[0].split('.')
            if len(left) > 1 and len(left[1]) > dec_places:
                left[1] = left[1][:dec_places]
            val = '.'.join(left)
    else:
        val = str(num)
    val = val.split('E')

    if len(val) == 1:
        return prepend + val[0] + append
    else:
        if val[1].startswith('+'):
            val[1] = str(int(val[1][1:]))
        return prepend + val[0] + '×10^' + val[1] + append

def to_ordinal(num):
    """ Returns a string representing the ordinal of num. """
    str_n = str(num)
    ones = num % 10
    if 1 <= ones <= 3 and num not in (11, 12, 13):
        if ones == 1:
            return str_n + 'st'
        elif ones == 2:
            return str_n + 'nd'
        else:
            return str_n + 'rd'
    else:
        return str_n + 'th'
