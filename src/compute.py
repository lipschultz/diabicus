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
import re
import logging

import simpleeval

DEFAULT_NONZERO_THRESHOLD = 1e-15

FUNCTION_PREFIX = '\u200b'

class ComputationError:
    '''
    Class to represent any parsing/computation/math error.
    '''
    def __init__(self, message):
        self.msg = message

EXPRESSION_TRANSLATIONS = {'×' : '*', '^': '**'}
def translate_operators(expr):
    """ Convert human-familiar operators to python operators. """
    for k, val in EXPRESSION_TRANSLATIONS.items():
        expr = expr.replace(k, val)
    return expr

def make_multiplying_variables_explicit(expr, variables):
    """ Convert implicit multiplication of variables to explicit. """
    #Need to ignore all variables between FUNCTION_PREFIX and '('
    variables = '|'.join(variables)
    start = 0
    new_expr = ''
    while start < len(expr):
        try:
            pos_func_prefix = expr.index(FUNCTION_PREFIX, start)
        except ValueError:
            pos_func_prefix = len(expr)
        try:
            pos_open_paren = expr.index('(', pos_func_prefix)
        except ValueError:
            pos_open_paren = len(expr)

        part = expr[start:pos_func_prefix+1]
        curr_len = len(part)
        part = re.sub('(%s)(%s|%s)' % (variables, variables, FUNCTION_PREFIX),
                      lambda m: m.group(1)+'*'+m.group(2), part
                     )
        new_len = len(part)
        while new_len != curr_len:
            curr_len = new_len
            part = re.sub('(%s)(%s|%s)' % (variables, variables, FUNCTION_PREFIX),
                          lambda m: m.group(1)+'*'+m.group(2), part
                         )
            new_len = len(part)

        new_expr += part + expr[pos_func_prefix+1:pos_open_paren+1]

        start = pos_open_paren+1
    return new_expr

def make_multiplication_explicit(expr, variables):
    """
    Convert implicit multiplication to explicit multiplication.

    Multiplication can be implied with:
    - parentheses, e.g. `3(5)2` = `3*(5)*2`
    - a number before/after a function, e.g. `3fn(2)4` = `3*fn(2)*4`
    - adjacent variables, e.g. `4e` = `4*e`
    """
    expr = re.sub('([0-9).])([^0-9).+*/-])', lambda m: m.group(1)+'*'+m.group(2), expr)
    expr = make_multiplying_variables_explicit(expr, variables)
    expr = re.sub('([^0-9(.+*/-]+)([0-9(.])',
                  lambda m: (
                      (m.group(1)[1:] if m.group(1).startswith(FUNCTION_PREFIX) else m.group(1)+'*')
                      +(m.group(2)[1:] if m.group(2).startswith(FUNCTION_PREFIX) else m.group(2))
                  ),
                  expr
                 )
    return expr

def remove_leading_zeros(expression):
    return re.sub(r'(\d+\.?\d*)', lambda res: strip_leading_zeros_from_number(res.group(1)), expression)

def strip_leading_zeros_from_number(number):
    number = number.lstrip('0')
    if len(number) == 0 or number[0] == '.':
        number = '0' + number
    return number

def round_to_int_if_close(value, threshold=DEFAULT_NONZERO_THRESHOLD):
    if isinstance(value, complex):
        return complex(round_to_int_if_close(value.real, threshold), round_to_int_if_close(value.imag, threshold))
    elif isinstance(value, float):
        ceil = math.ceil(value)
        floor = math.floor(value)
        if abs(value - ceil) < threshold:
            return ceil
        elif abs(value - floor) < threshold:
            return floor
        else:
            return value
    else:
        return value

def convert_complex_with_0_imag_to_real(value):
    if isinstance(value, complex) and abs(value.imag) < DEFAULT_NONZERO_THRESHOLD:
        return value.real
    else:
        return value

def convert_result(value, *, round_int_threshold=DEFAULT_NONZERO_THRESHOLD):
    value = round_to_int_if_close(value)
    return convert_complex_with_0_imag_to_real(value)

def eval_expr(evaluator, expr):
    """
    Convert expr into something evaluator can evaluate, compute and return result.
    """
    expr = translate_operators(expr)
    expr = make_multiplication_explicit(expr, evaluator.names)
    expr = remove_leading_zeros(expr)
    expr = expr.replace(FUNCTION_PREFIX, '')

    try:
        value = evaluator.eval(expr)
        value = round_to_int_if_close(value)
        return convert_complex_with_0_imag_to_real(value)
    except SyntaxError:
        return ComputationError('invalid syntax')
    except ZeroDivisionError:
        return ComputationError('divide by zero')
    except (simpleeval.NumberTooHigh, OverflowError) as err:
        logging.error('eval_expr: Error evaluating expression: '+str(err))
        return ComputationError("Overflow error")
    except Exception as err:  #pragma: no cover
        logging.error('eval_expr: Error evaluating expression ('+str(type(err))+'): '+str(err))
        return ComputationError('computation error')
