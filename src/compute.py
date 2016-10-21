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
    def __init__(self, message):
        self.msg = message

EXPRESSION_TRANSLATIONS = {'×' : '*', '^': '**'}
def translate_operators(expr):
    for k, v in EXPRESSION_TRANSLATIONS.items():
        expr = expr.replace(k, v)
    return expr

def make_multiplying_variables_explicit(expr, variables):
    #Need to ignore all variables between FUNCTION_PREFIX and '('
    variables = '|'.join(variables)
    start = 0
    new_expr = ''
    while start < len(expr):
        try:
            pos_func_prefix = expr.index(FUNCTION_PREFIX, start)
        except:
            pos_func_prefix = len(expr)
        try:
            pos_open_paren = expr.index('(', pos_func_prefix)
        except:
            pos_open_paren = len(expr)

        part = expr[start:pos_func_prefix+1]
        curr_len = len(part)
        part = re.sub('(%s)(%s|%s)' % (variables, variables, FUNCTION_PREFIX), lambda m: m.group(1)+'*'+m.group(2), part)
        new_len = len(part)
        while new_len != curr_len:
            curr_len = new_len
            part = re.sub('(%s)(%s|%s)' % (variables, variables, FUNCTION_PREFIX), lambda m: m.group(1)+'*'+m.group(2), part)
            new_len = len(part)

        new_expr += part + expr[pos_func_prefix+1:pos_open_paren+1]

        start = pos_open_paren+1
    return new_expr

def make_operations_explicit(expr, variables):
    expr = re.sub('([0-9).])([^0-9).+*/-])', lambda m: m.group(1)+'*'+m.group(2), expr)
    expr = re.sub('([^0-9(.+*/-]+)([0-9(.])', lambda m: m.group(1)+('' if FUNCTION_PREFIX in m.group(1) else '*')+m.group(2), expr)
    expr = make_multiplying_variables_explicit(expr, variables)
    return expr

def eval_expr(evaluator, expr):
    expr = translate_operators(expr)
    expr = make_operations_explicit(expr, evaluator.names)
    expr = expr.replace(FUNCTION_PREFIX, '')

    try:
        return evaluator.eval(expr)
    except SyntaxError:
        return ComputationError('invalid syntax')
    except ZeroDivisionError:
        return ComputationError('divide by zero')
    except (simpleeval.NumberTooHigh, OverflowError) as e:
        logging.error('Error evaluating expression: '+str(e))
        return ComputationError("Overflow error")
    except Exception as e:
        logging.error('Error evaluating expression ('+str(type(e))+'): '+str(e))
        return ComputationError('computation error')

