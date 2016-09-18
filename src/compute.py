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

def make_operations_explicit(expr):
    expr = re.sub(r'([0-9).])\(', lambda m: m.group(1)+'*(', expr)
    expr = re.sub(r'\)([0-9(.])', lambda m: ')*'+m.group(1), expr)
    expr = re.sub('([0-9).]|(?:Ans))'+FUNCTION_PREFIX, lambda m: m.group(1)+'*', expr)
    expr = re.sub('Ans([0-9(.])', lambda m: 'Ans*'+m.group(1), expr)
    expr = re.sub('([0-9).])Ans', lambda m: m.group(1)+'*Ans', expr)
    expr = expr.replace('AnsAns', 'Ans*Ans')
    return expr

def eval_expr(evaluator, expr):
    expr = translate_operators(expr)
    expr = make_operations_explicit(expr)
    expr = expr.replace(FUNCTION_PREFIX, '')

    try:
        return evaluator.eval(expr)
    except SyntaxError:
        return ComputationError('invalid syntax')
    except ZeroDivisionError:
        return ComputationError('divide by zero')
    except simpleeval.NumberTooHigh as e:
        logging.error('Error evaluating expression: '+str(e))
        return ComputationError("Calculation timeout")
    except Exception as e:
        logging.error('Error evaluating expression: '+str(e))
        return ComputationError('computation error')

