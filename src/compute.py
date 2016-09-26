import re
import logging
import simpleeval

FUNCTION_PREFIX = '\u200b'

class ComputationError:
    def __init__(self, message):
        self.msg = message

EXPRESSION_TRANSLATIONS = {'×' : '*', '^': '**'}
def translate_operators(expr):
    for k, v in EXPRESSION_TRANSLATIONS.items():
        expr = expr.replace(k, v)
    return expr

def make_operations_explicit(expr, variables):
    variables = '|'.join(variables)
    expr = re.sub('([0-9).])([^0-9).+*/-])', lambda m: m.group(1)+'*'+m.group(2), expr)
    expr = re.sub('([^0-9(.+*/-]+)([0-9(.])', lambda m: m.group(1)+('' if FUNCTION_PREFIX in m.group(1) else '*')+m.group(2), expr)
    expr = re.sub('(%s)(%s|%s)' % (variables, variables, FUNCTION_PREFIX), lambda m: m.group(1)+'*'+m.group(2), expr)
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

