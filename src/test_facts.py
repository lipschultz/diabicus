import number_facts
import math
from simpleeval import SimpleEval
import compute
import time
from itertools import chain
import time_limit

general_eval = SimpleEval()
general_eval.functions['ln'] = math.log
general_eval.names['π'] = math.pi
general_eval.names['τ'] = 2*math.pi
general_eval.names['e'] = math.e
general_eval.names['i'] = number_facts.I
general_eval.names['φ'] = number_facts.GOLDEN_RATIO

TAG_BIGNUM = 'big-num'

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
            {'result' : 1e35, 'tags' : (TAG_BIGNUM, )},
            {'result' : -1},
            {'result' : -2},
            {'result' : -0.5},
            {'result' : -13.7},
            {'result' : -1e-35},
            {'result' : -1e35},
            {'result' : complex(3, 1)},
            {'result' : (45, complex(6, 17.079468445347132j), 88)},
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
            {'formula' : ('eiτ×5', '15-2')},
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

def test_file(filename):
    facts = number_facts.load_json_file(filename)
    print('Total facts:', len(facts))

    fact_results = []
    for fact in facts:
        fact_results.append(test_fact(fact))
    return fact_results

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
                raw_msg = fact.raw_message[i]
                try:
                    start = time.time()
                    msg_text = timed_exec.run(msg, formula, result, context)
                    duration = time.time() - start
                    success = True
                    if len(msg_text) > 100:
                        print(repr(fact), 'failed on msg', i, '('+msg_text+') with test case', case, ': text too long (' + str(len(msg_text)) + ')')
                        success = False
                    status.add_msg_result(case, i, True, duration)
                except TimeoutError as e:
                    if not ('tags' in case and TAG_BIGNUM in case['tags']):
                        print(repr(fact), 'timed out on msg', i, '('+raw_msg+') with test case', case)
                        status.add_msg_result(case, i, False)
                except OverflowError as e:
                    if not ('tags' in case and TAG_BIGNUM in case['tags']):
                        print(repr(fact), 'encountered overflow on msg', i, '('+raw_msg+') with test case', case)
                        status.add_msg_result(case, i, False)
                except Exception as e:
                    print(repr(fact), 'failed on msg', i, '('+raw_msg+') with test case', case, ':', type(e), e)
                    status.add_msg_result(case, i, False)

    return status

def convert_test_case(test_case):
    result = test_case.get('result')
    formula = test_case.get('formula')
    context = test_case.get('context')

    if context is None:
        if formula is None:
            if not hasattr(result, '__iter__') or isinstance(result, str):
                result = (result, )
            formula = [str(r) for r in result]
        elif result is None:
            if not hasattr(formula, '__iter__') or isinstance(formula, str):
                formula = (formula, )
            result = [compute.eval_expr(general_eval, f) for f in formula]
        context = {'result' : result, 'formula' : formula}

    return formula, result, context

if __name__ == '__main__':
    results = test_file('../resources/youtube.json')
    times = list(chain.from_iterable((r.test_times().values() for r in results)))
    print('Test time: avg=%0.2g, max=%0.2g, min=%0.2g' % (sum(times)/len(times), max(times), min(times)))

    test_failures = len([s for r in results for s in r.cases.values() if not s['success']])
    test_total = len([s for r in results for s in r.cases.values()])
    print('Test Failures: %d / %d = %0.2f' % (test_failures, test_total, test_failures/test_total))

    msg_failures = len([c for r in results for s in r.msgs.values() for c in s.values() if not c['success']])
    msg_total = len([c for r in results for s in r.msgs.values() for c in s.values()])
    print('Message Failures: %d / %d = %0.2f' % (msg_failures, msg_total, msg_failures/msg_total))
