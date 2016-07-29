import math
import scipy.integrate
from fractions import Fraction
import json
import sys
import random
import logging

def context_to_str(context):
    str_context = []
    for k, v in context.items():
        if isinstance(v, (list, tuple)):
            item = '<' + str(v[-5:]) + '>'
        else:
            item = repr(v)
        str_context.append(k + ' : ' + str(item))

    return '{' + ', '.join(str_context) + '}'

def is_int(val):
    return isinstance(val, int) or (isinstance(val, float) and val % 1 == 0)

def is_rational(val):
    return isinstance(val, (int, float))

def is_number(val):
    return isinstance(val, (int, float, complex))

def is_error(val):
    pass

PRIME_NUMBERS = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]
def is_prime(number):
    return is_int(number) and number > 1 and number in PRIME_NUMBERS

def is_surreal(number):
    return False

FIBONACCI_NUMBERS = (0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765)
LUCAS_NUMBERS = (2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322, 521, 843, 1364, 2207, 3571, 5778, 9349, 15127, 24476, 39603, 64079, 103682, 167761, 271443, 439204, 710647, 1149851, 1860498, 3010349, 4870847, 7881196, 12752043, 20633239, 33385282)
def is_subsequence_of(needle, haystack):
    for offset in (i for i, x in enumerate(haystack) if x == needle[0]):
        if offset + len(needle) > len(haystack):
            return False

        matches = [needle[i] == haystack[offset+i] for i in range(1, len(needle))]

        if len(matches) == len(needle)-1 and all(matches):
            return True

    return False

def is_close(num1, num2, threshold=1e-5):
    return abs(num1-num2) < threshold



def farey_addition(history):
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

    def test(self, formula, result, history):
        return not self.skip and is_int(result) and 21 <= result <= 65

    def message(self, formula, result, history):
        row1 = [result-20, 1, 12, 7]
        row2 = [11, 8, result-21, 2]
        row3 = [5, 10, 3, result-18]
        row4 = [4, result-19, 6, 9]
        square = [row1, row2, row3, row4]
        return 'The magic square for %d is %s' % (result, square)

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
        self.message = json_data.get('msg', self.title)

        try:
            self.init = compile(self.init, '<json_string>', "exec")
            eval(self.init)
        except:
            pass

        try:
            self.test = eval(self.raw_test)
        except:
            self.test = False
        if not callable(self.test):
            self.test = lambda *args: False

        try:
            self.message = eval(self.message)
        except:
            pass
        if not callable(self.message):
            self.message = lambda formula, result, history: self.message % {'result' : result}

    def __str__(self):
        return self.title

    def __repr__(self):
        return str(self) + "{test : " + repr(self.raw_test.encode("unicode-escape")) + "}"

def load_json_file(json_file):
    with open(json_file) as fin:
        contents = json.load(fin)

    facts = [JsonFact(d) for d in contents]
    return facts

def test_fact(fact, formula, result, context):
    try:
        logging.debug("Testing fact " + repr(fact) + " with context " + context_to_str(context))
        result = fact.test(formula, result, context)
        logging.debug("Test result for " + repr(fact) + ": " + str(result))
        return result
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
    logging.info("Picking random fact from: "+repr(facts))

    total = sum(f.weight for f in facts)
    if total == 0:
        logging.info('No facts to pick')
        return None

    p = random.uniform(0, total)
    cdf = 0
    for f in facts:
        cdf += f.weight
        if p <= cdf:
            logging.info('Picking fact: ' + str(f))
            return f

    f = random.choice(facts)
    logging.info('Picking fact (fallback): ' + str(f))
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
