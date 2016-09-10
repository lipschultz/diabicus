import number_facts
import math
from simpleeval import SimpleEval
import compute

general_eval = SimpleEval()

TEST_SET = [{'result' : 0},
            {'result' : 1},
            {'result' : 2},
            {'result' : number_facts.GOLDEN_RATIO},
            {'result' : number_facts.PRIME_NUMBERS[15]},
            {'result' : number_facts.FIBONACCI_NUMBERS[15]},
            {'result' : number_facts.LUCAS_NUMBERS[15]},
            {'result' : math.pi},
            {'result' : math.e},
            {'result' : math.inf},
            {'result' : math.pi + 1.643e-8},
            {'result' : math.e + 1.643e-8},
            {'result' : 0.5},
            {'result' : 13.7},
            {'result' : 1e-35},
            {'result' : 1e35},
            {'result' : -1},
            {'result' : -2},
            {'result' : -0.5},
            {'result' : -13.7},
            {'result' : -1e-35},
            {'result' : -1e35},
            {'result' : complex(0, 5), 'formula' : '(-25)^0.5'},
            {'result' : complex(0, -5), 'formula' : '-(-25)^0.5'},
            {'result' : complex(3, 5), 'formula' : '3+(-25)^0.5'},
            {'result' : complex(-3, -5), 'formula' : '-3-(-25)^0.5'},
            {'result' : complex(-3, 5), 'formula' : '-3+(-25)^0.5'},
            {'result' : complex(3, -5), 'formula' : '3-(-25)^0.5'},
            {'formula' : '1/0'},
            {'formula' : '9**/5'},
            ]
'''
[WARNING] [Math Jokes Explained threw exception TypeError("unsupported operand type(s) for //] 'int' and 'ComputationError'",): formula = "Ans+2", result = "1382041022933, context = {formula : <['105×17', 'Ans^3', '(Ans-8)×3^5', '1/0', 'Ans+2']>, result : <[1785, 5687411625, 1382041022931, <compute.ComputationError object at 0xb202610c>, 1382041022933]>, output : <['1785', '5.6874116e+09', '1.382041e+12', 'Error: divide by zero', '1.382041e+12']>}
'''

def test_file(filename):
    facts = number_facts.load_json_file(filename)
    print('Total facts:', len(facts))

    for fact in facts:
        test_fact(fact)

def test_fact(fact):
    if not isinstance(fact.weight, (int, float)):
        print(repr(fact), 'has non-numeric weight:', fact.weight)

    for case in TEST_SET:
        formula, result, context = convert_test_case(case)
        try:
            test_result = fact.test(formula, result, context)
        except Exception as e:
            print(repr(fact), 'failed on test case', case, ':', e)
            return False

        if test_result:
            had_failure = False
            for i in range(len(fact._message)):
                msg = fact._message[i]
                try:
                    msg(formula, result, context)
                except Exception as e:
                    raw_msg = fact.raw_message[i]
                    print(repr(fact), 'failed on msg', i, '('+raw_msg+'):', e)
                    had_failure = True

            return not had_failure

    return True

def convert_test_case(test_case):
    result = test_case.get('result')
    formula = test_case.get('formula')
    context = test_case.get('context')

    if context is None:
        if formula is None:
            formula = str(result)
        elif result is None:
            result = compute.eval_expr(general_eval, formula)
        context = {'result' : [result], 'formula' : [formula]}

    return formula, result, context

if __name__ == '__main__':
    test_file('../resources/youtube.json')
