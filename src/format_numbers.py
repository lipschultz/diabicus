import sys
import decimal
import math

from . import numeric_tools

def simplify_complex(value, real_nonzero_threshold=1e-15, imag_nonzero_threshold=None):
    if imag_nonzero_threshold is None:
        imag_nonzero_threshold = real_nonzero_threshold

    real = value.real if abs(value.real) >= real_nonzero_threshold else 0

    if abs(value.imag) < imag_nonzero_threshold:
        return real
    else:
        return complex(real, value.imag)

def pretty_print_complex(value, real_tostr_fn=lambda v: str(v), imag_tostr_fn=None, imaginary_indicator='i', display_0=False):
    if imag_tostr_fn is None:
        imag_tostr_fn = real_tostr_fn

    real = real_tostr_fn(value.real)
    imag = imag_tostr_fn(value.imag)

    if display_0 or (value.imag != 0 and value.real != 0):
        return '%s + %s%s' % (real, imag, imaginary_indicator)
    elif value.imag == 0:
        return real
    else:
        return '%s%s' % (imag, imaginary_indicator)

def to_pretty_x10(n, dec_places=5, prepend='', append=''):
    if n < sys.float_info.min or n > sys.float_info.max:
        val = decimal.Decimal(n)
        decimal.getcontext().prec = dec_places+1
        val = str(val.normalize())
    elif not numeric_tools.is_int(n) or math.log10(n) > 10:
        val = ('%0.'+str(dec_places+1)+'G') % n
        v = val.split('E')
        if len(v) == 1:
            left = v[0].split('.')
            if len(left) > 1 and len(left[1]) > dec_places:
                left[1] = left[1][:dec_places]
            val = '.'.join(left)
    else:
        val = str(n)
    val = val.split('E')

    if len(val) == 1:
        return prepend + val[0] + append
    else:
        if val[1].startswith('+'):
            val[1] = str(int(val[1][1:]))
        return prepend + val[0] + '×10^' + val[1] + append

def to_ordinal(n):
    str_n = str(n)
    ones = n % 10
    if 1 <= ones <= 3 and n not in (11, 12, 13):
        if ones == 1:
            return str_n + 'st'
        elif ones == 2:
            return str_n + 'nd'
        else:
            return str_n + 'rd'
    else:
        return str_n + 'th'
