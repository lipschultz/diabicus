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
import time
from itertools import chain
import os
import importlib

from simpleeval import SimpleEval

from src import number_facts
from src import numeric_tools
from src import compute
from src import time_limit

general_eval = SimpleEval()
general_eval.functions['ln'] = lambda n: math.log(compute.convert_result(n))
general_eval.functions['sin'] = lambda n: math.sin(compute.convert_result(n))
general_eval.functions['cos'] = lambda n: math.cos(compute.convert_result(n))
general_eval.functions['tan'] = lambda n: math.tan(compute.convert_result(n))
general_eval.names['π'] = math.pi
general_eval.names['τ'] = 2*math.pi
general_eval.names['e'] = math.e
general_eval.names['i'] = numeric_tools.I
general_eval.names['φ'] = numeric_tools.GOLDEN_RATIO

TAG_BIGNUM = 'big-num'

TEST_SET = [{'result' : 0},
            {'result' : 1},
            {'result' : 2},
            {'result' : numeric_tools.GOLDEN_RATIO},
            {'result' : numeric_tools.PRIME_NUMBERS[15]},
            {'result' : numeric_tools.FIBONACCI_NUMBERS[15]},
            {'result' : numeric_tools.LUCAS_NUMBERS[15]},
            {'result' : math.pi},
            {'result' : math.e},
            {'result' : math.inf},
            {'result' : math.pi + 1.643e-8},
            {'result' : math.e + 1.643e-8},
            {'result' : 0.5},
            {'result' : 13.7},
            {'result' : 1e-35},
            {'result' : 1e35, 'tags' : (TAG_BIGNUM, )},
            {'result' : -1},
            {'result' : -2},
            {'result' : -0.5},
            {'result' : -13.7},
            {'result' : -1e-35},
            {'result' : -1e35},
            {'result' : complex(3, 1)},
            {'result' : (88, complex(6, 17.079468445347132), 45)},
            {'result' : (0, 0, 0, 0, 0)},
            {'formula' : '(-25)^0.5'},
            {'formula' : '-(-25)^0.5'},
            {'formula' : '3+(-25)^0.5'},
            {'formula' : '-3-(-25)^0.5'},
            {'formula' : '-3+(-25)^0.5'},
            {'formula' : '3-(-25)^0.5'},
            {'formula' : '1/0'},
            {'formula' : '9**/5'},
            {'formula' : '.3^-221.062', 'tags' : (TAG_BIGNUM, )},
            {'formula' : '1213^3', 'tags' : (TAG_BIGNUM, )},
            {'formula' : '333×2197-​ln(.5)'},
            {'formula' : ('15-2', 'eiτ×5')},
            {'formula' : ('1i', 'Ans+3', 'Ans^2', '(Ans)^.5')},
            {'formula' : ('14i×-i', '​ln(Ans)')},
            {'formula' : '​ln(14i×-i)'},
            ]

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

def get_loader_lib(module_location):
    path, name = os.path.split(module_location)
    module_name = os.path.splitext(name)[0]
    module_path = path
    importlib.import_module(module_path)
    return importlib.import_module('.'+module_name, module_path)

def test_file(filename):
    facts_lib = get_loader_lib(filename)
    facts = facts_lib.load_facts()

    fact_results = []
    for fact in facts:
        fact_results.append(test_fact(fact))
    return fact_results

def fact_to_str(fact, max_len=100):
    return repr(fact)[:max_len]

def test_fact(fact):
    TIMEOUT = 3
    timed_exec = time_limit.TimedExecution(TIMEOUT)
    status = TestResult(fact)
    if not isinstance(fact.weight, (int, float)):
        print(repr(fact), 'has non-numeric weight:', fact.weight)
        status.weight = False

    #print(fact)
    for case in TEST_SET:
        #print('\t', case)
        formula, result, context = convert_test_case(case)

        try:
            start = time.time()
            test_result = timed_exec.run(fact.test, formula, result, context)
            duration = time.time() - start
            status.add_test_case_result(case, True, duration)
        except TimeoutError as e:
            if not ('tags' in case and TAG_BIGNUM in case['tags']):
                print('test: timeout error ('+str(e)+')\n\tfact:', fact_to_str(fact), '\n\tcase', case)
                status.add_test_case_result(case, False, TIMEOUT)
            test_result = False
        except Exception as e:
            print('test:', type(e), e, "\n\tfact:", fact_to_str(fact), '\n\tcase:', case)
            status.add_test_case_result(case, False)
            test_result = False

        if test_result:
            for i in range(len(fact._messages)):
                #print('\tmsg:', i)
                msg = fact._messages[i]
                raw_msg = fact.raw_message[i]
                try:
                    start = time.time()
                    msg_text = timed_exec.run(msg, formula, result, context)
                    duration = time.time() - start
                    success = True
                    if len(msg_text) > 100:
                        print('msg: length error:', len(msg_text), '\n\tfact:', fact_to_str(fact), '\n\tmsg', i, ': '+msg_text+'\n\tcase:', case)
                        success = False
                    status.add_msg_result(case, i, True, duration)
                except TimeoutError as e:
                    if not ('tags' in case and TAG_BIGNUM in case['tags']):
                        print('msg: timeout error ('+str(e)+')\n\tfact:', fact_to_str(fact), '\n\tmsg', i, ': '+raw_msg+'\n\tcase:', case)
                        status.add_msg_result(case, i, False)
                except OverflowError as e:
                    if not ('tags' in case and TAG_BIGNUM in case['tags']):
                        print('msg: overflow error ('+str(e)+')\n\tfact:', fact_to_str(fact), '\n\tmsg', i, ': '+raw_msg+'\n\tcase:', case)
                        status.add_msg_result(case, i, False)
                except Exception as e:
                    print('msg:', type(e), e, "\n\tfact:", fact_to_str(fact), '\n\tmsg', i, ': '+raw_msg+'\n\tcase:', case)
                    status.add_msg_result(case, i, False)

    return status

def convert_test_case(test_case):
    result = test_case.get('result')
    formula = test_case.get('formula')
    context = test_case.get('context')

    if result is not None and (not hasattr(result, '__iter__') or isinstance(result, str)):
        result = (result, )
    if formula is not None and (not hasattr(formula, '__iter__') or isinstance(formula, str)):
        formula = (formula, )

    if context is None:
        if formula is None:
            formula = [str(r) for r in result]
        elif result is None:
            result = []
            general_eval.names['Ans'] = 0
            for f in formula:
                r = compute.eval_expr(general_eval, f)
                result.append(r)
                general_eval.names['Ans'] = r
        context = {'result' : result, 'formula' : formula}

    return formula[-1], result[-1], context

if __name__ == '__main__':
    results = test_file('resources/youtube_facts.py')
    print('Facts loaded:', len(results))

    times = list(chain.from_iterable((r.test_times().values() for r in results)))
    print('Test time: avg=%0.2g, max=%0.2g, min=%0.2g' % (sum(times)/len(times), max(times), min(times)))

    test_failures = len([s for r in results for s in r.cases.values() if not s['success']])
    test_total = len([s for r in results for s in r.cases.values()])
    print('Test Failures: %d / %d = %0.2f%%' % (test_failures, test_total, test_failures/test_total*100))

    msg_failures = len([c for r in results for s in r.msgs.values() for c in s.values() if not c['success']])
    msg_total = len([c for r in results for s in r.msgs.values() for c in s.values()])
    print('Message Failures: %d / %d = %0.2f%%' % (msg_failures, msg_total, msg_failures/msg_total*100))
