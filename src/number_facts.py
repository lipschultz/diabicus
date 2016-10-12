import math
import scipy.integrate
from fractions import Fraction
import json
import sys
import random
import logging
import string
import re
import time_limit

def context_to_str(context):
    str_context = []
    for k, v in context.items():
        if isinstance(v, (list, tuple)):
            item = '<' + str(v[-5:]) + '>'
        else:
            item = repr(v)
        str_context.append(k + ' : ' + str(item))

    return '{' + ', '.join(str_context) + '}'


def farey_addition(history):
    if len(history['result']) < 3:
        return False
    first = Fraction(history['result'][-3]).limit_denominator(234)
    second = Fraction(history['result'][-2]).limit_denominator(234)
    third = Fraction(history['result'][-1]).limit_denominator(234)
    return Fraction(first.numerator + third.numerator, first.denominator + third.denominator) == second

class MagicSquare:
    def __init__(self):
        self.link = 'https://www.youtube.com/watch?v=aQxCnmhqZko'
        self.title = 'Magic Square Party Trick'
        self.source = 'Numberphile'
        self.skip = True

        self.__coeff = 1/(4*math.sqrt(3))
        self.__exp = math.pi*math.sqrt(2/3)

    def test(self, formula, result, context):
        return not self.skip and is_int(result) and 21 <= result <= 65

    def message(self, formula, result, context):
        row1 = [result-20, 1, 12, 7]
        row2 = [11, 8, result-21, 2]
        row3 = [5, 10, 3, result-18]
        row4 = [4, result-19, 6, 9]
        square = [row1, row2, row3, row4]
        return 'The magic square for %d is %s' % (result, square)

DEFAULT_MSG_FORMATTER = string.Formatter()

class JsonFact:
    def __init__(self, json_data):
        self.link = json_data.get('link')
        self.title = json_data.get('title')
        self.source = json_data.get('source')
        self.oeis = json_data.get('oeis')
        self.wiki = json_data.get('wiki')
        self.weight = json_data.get('weight', 1)
        self.init = json_data.get('init')
        self.raw_test = json_data.get('test')
        self.raw_message = json_data.get('msg', self.title)

        try:
            self.init = compile(self.init, '<json_string>', "exec")
            print("eval result for", self.title, ":", eval(self.init, globals(), locals()))
        except:
            pass

        try:
            self.test = eval(self.raw_test)
        except:
            self.test = False
        if not callable(self.test):
            self.test = lambda *args: False

        if not isinstance(self.raw_message, list):
            self.raw_message = [self.raw_message]

        self._message = []
        for i in range(len(self.raw_message)):
            raw_msg = self.raw_message[i]
            try:
                msg = eval(raw_msg)
            except:
                msg = raw_msg
            if not callable(msg):
                msg = lambda formula, result, context: DEFAULT_MSG_FORMATTER.format(raw_msg, formula=formula, result=result, context=context)

            self._message.append(msg)

    def message(self, formula, result, context):
        msg = random.choice(self._message)
        try:
            return msg(formula, result, context)
        except OverflowError as e:
            logging.warning("Encountered overflow error for fact "+str(self)+", message " + msg + ", formula="+formula+", result="+result+", context="+context_to_str(context))
            return self.title

    def __str__(self):
        return self.title

    def __repr__(self):
        return str(self) + "{test : " + repr(self.raw_test.encode("unicode-escape")) + "}"

def load_json_file(json_file):
    with open(json_file) as fin:
        contents = json.load(fin)

    facts = [JsonFact(d) for d in contents]
    logging.info(str(len(facts)) + ' facts loaded from ' + json_file)
    return facts

def test_fact(fact, formula, result, context):
    timed_exec = time_limit.TimedExecution()
    try:
        logging.debug("Testing fact " + repr(fact) + " with context " + context_to_str(context))
        result = timed_exec.run(fact.test, formula, result, context)
        logging.debug("Test result for " + repr(fact) + ": " + str(result))
        return result
    except TimeoutError as e:
        logging.warning(str(fact) + ' timed out on formula = "'+formula+'", result = "' + str(result) + ', context = ' + context_to_str(context))
    except Exception as e:
        logging.warning(str(fact) + ' threw exception ' + repr(e) + ': formula = "'+formula+'", result = "' + str(result) + ', context = ' + context_to_str(context))

    return False

def find_applicable_facts(facts, formula, result, context):
    app_facts = []
    for f in facts:
        if test_fact(f, formula, result, context):
            app_facts.append(f)

    logging.info("Number of applicable facts found: "+str(len(app_facts)))
    return app_facts

def pick_random_fact(facts):
    logging.info("Pick random fact from: "+repr(facts))

    total = sum(f.weight for f in facts)
    if total == 0:
        logging.info('No facts to pick')
        return None

    p = random.uniform(0, total)
    cdf = 0
    for f in facts:
        cdf += f.weight
        if p <= cdf:
            logging.info('Fact picked: ' + str(f))
            return f

    f = random.choice(facts)
    logging.info('Fact picked (fallback): ' + str(f))
    return f

def get_fact(facts, formula, result, context):
    app_facts = find_applicable_facts(facts, formula, result, context)
    rand_fact = pick_random_fact(app_facts)
    return rand_fact

if __name__ == '__main__':
    facts = load_json_file('../resources/youtube.json')
    formula = 'cos(2)'
    result = 19
    context = {'result' : [15, 14, 13, 12]}
    rand_fact = get_fact(facts, formula, result, context)

    print('chose: ' + str(rand_fact))
