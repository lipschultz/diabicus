import number_facts
import math
from simpleeval import SimpleEval
import compute
import time
from itertools import chain

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
            {'formula' : '(-25)^0.5'},
            {'formula' : '-(-25)^0.5'},
            {'formula' : '3+(-25)^0.5'},
            {'formula' : '-3-(-25)^0.5'},
            {'formula' : '-3+(-25)^0.5'},
            {'formula' : '3-(-25)^0.5'},
            {'formula' : '1/0'},
            {'formula' : '9**/5'},
            ]
'''
[WARNING] [Math Jokes Explained threw exception TypeError("unsupported operand type(s) for //] 'int' and 'ComputationError'",): formula = "Ans+2", result = "1382041022933, context = {formula : <['105×17', 'Ans^3', '(Ans-8)×3^5', '1/0', 'Ans+2']>, result : <[1785, 5687411625, 1382041022931, <compute.ComputationError object at 0xb202610c>, 1382041022933]>, output : <['1785', '5.6874116e+09', '1.382041e+12', 'Error: divide by zero', '1.382041e+12']>}
'''

import signal
class timeout:
    '''
    http://stackoverflow.com/questions/2281850/timeout-function-if-it-takes-too-long-to-finish/22348885#22348885
    see also:
        https://stackoverflow.com/questions/15528939/python-3-timed-input
        http://stackoverflow.com/questions/492519/timeout-on-a-function-call
        http://stackoverflow.com/questions/2281850/timeout-function-if-it-takes-too-long-to-finish
    '''
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

class TestResult:
    def __init__(self, fact):
        self.fact = fact
        self.weight = True
        self.cases = {}
        self.msgs = {}
        self.success = True

    def add_test_case_result(self, case, success, duration=None):
        case = tuple(sorted(case.items()))
        self.cases[case] = {'success' : success, 'duration' : duration}
        self.success = self.success and success

    def add_msg_result(self, case, msg_i, success, duration=None):
        case = tuple(sorted(case.items()))
        case_msgs = self.msgs.get(case, {})
        case_msgs[msg_i] = {'success' : success, 'duration' : duration}
        self.msgs[case] = case_msgs
        self.success = self.success and success

    def test_times(self):
        return dict([(k, v['duration']) for k, v in self.cases.items() if v['duration'] is not None])

def test_file(filename):
    facts = number_facts.load_json_file(filename)
    print('Total facts:', len(facts))

    fact_results = []
    for fact in facts:
        fact_results.append(test_fact(fact))
    return fact_results

def test_fact(fact):
    TIMEOUT = 3
    status = TestResult(fact)
    if not isinstance(fact.weight, (int, float)):
        print(repr(fact), 'has non-numeric weight:', fact.weight)
        status.weight = False

    #print(fact)
    for case in TEST_SET:
        #print('\t', case)
        formula, result, context = convert_test_case(case)
        try:
            with timeout(seconds=TIMEOUT):
                start = time.time()
                test_result = fact.test(formula, result, context)
                duration = time.time() - start
                status.add_test_case_result(case, True, duration)
        except TimeoutError as e:
            print(repr(fact), 'timed out on case', case)
            status.add_test_case_result(case, False, TIMEOUT)
            test_result = False
        except Exception as e:
            print(repr(fact), 'failed on test case', case, ':', e)
            status.add_test_case_result(case, False)
            test_result = False

        if test_result:
            for i in range(len(fact._message)):
                #print('\tmsg:', i)
                msg = fact._message[i]
                try:
                    start = time.time()
                    msg(formula, result, context)
                    duration = time.time() - start
                    status.add_msg_result(case, i, True, duration)
                except Exception as e:
                    raw_msg = fact.raw_message[i]
                    print(repr(fact), 'failed on msg', i, '('+raw_msg+') with test case', case, ':', e)
                    status.add_msg_result(case, i, False)

    return status

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
    results = test_file('../resources/youtube.json')
    times = list(chain.from_iterable((r.test_times().values() for r in results)))
    print('Test time: avg=%0.2g, max=%0.2g, min=%0.2g' % (sum(times)/len(times), max(times), min(times)))
