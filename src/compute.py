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

import re
import logging

from . import simpleeval

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

def eval_expr(evaluator, expr):
    """
    Convert expr into something evaluator can evaluate, compute and return result.
    """
    expr = translate_operators(expr)
    expr = make_multiplication_explicit(expr, evaluator.names)
    expr = expr.replace(FUNCTION_PREFIX, '')

    try:
        return evaluator.eval(expr)
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
