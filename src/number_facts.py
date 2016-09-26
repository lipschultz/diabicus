import math
import scipy.integrate
from fractions import Fraction
import decimal
import json
import sys
import random
import logging
import string
from functools import reduce
import re
from compute import ComputationError
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

def is_int(val):
    return isinstance(val, int) or (isinstance(val, float) and val % 1 == 0)

def is_rational(val):
    return isinstance(val, (int, float)) and not is_irrational(val)

def is_irrational(val):
    return is_transcendental(val) or val in {2**.5, GOLDEN_RATIO}

def is_transcendental(val):
    return val in (math.pi, math.e)

def is_real(val):
    return isinstance(val, (int, float))

def is_complex(val):
    return isinstance(val, complex)

def is_surreal(number):
    return False

def is_number(val):
    return isinstance(val, (int, float, complex))

def is_error(val):
    return isinstance(val, ComputationError)

GOLDEN_RATIO = (1 + 5**0.5) / 2
GRAHAMS_NUMBER = False
I = complex(0, 1)

PI_DIGITS = (3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4, 6, 2, 6, 4, 3, 3, 8, 3, 2, 7, 9, 5, 0, 2, 8, 8, 4, 1, 9, 7, 1, 6, 9, 3, 9, 9, 3, 7, 5, 1, 0, 5, 8, 2, 0, 9, 7, 4, 9, 4, 4, 5, 9, 2, 3, 0, 7, 8, 1, 6, 4, 0, 6, 2, 8, 6, 2, 0, 8, 9, 9, 8, 6, 2, 8, 0, 3, 4, 8, 2, 5, 3, 4, 2, 1, 1, 7, 0, 6, 7, 9, 8, 2, 1, 4)
PRIME_NUMBERS = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249, 1259, 1277, 1279, 1283, 1289, 1291, 1297, 1301, 1303, 1307, 1319, 1321, 1327, 1361, 1367, 1373, 1381, 1399, 1409, 1423, 1427, 1429, 1433, 1439, 1447, 1451, 1453, 1459, 1471, 1481, 1483, 1487, 1489, 1493, 1499, 1511, 1523, 1531, 1543, 1549, 1553, 1559, 1567, 1571, 1579, 1583, 1597, 1601, 1607, 1609, 1613, 1619, 1621, 1627, 1637, 1657, 1663, 1667, 1669, 1693, 1697, 1699, 1709, 1721, 1723, 1733, 1741, 1747, 1753, 1759, 1777, 1783, 1787, 1789, 1801, 1811, 1823, 1831, 1847, 1861, 1867, 1871, 1873, 1877, 1879, 1889, 1901, 1907, 1913, 1931, 1933, 1949, 1951, 1973, 1979, 1987, 1993, 1997, 1999, 2003, 2011, 2017, 2027, 2029, 2039, 2053, 2063, 2069, 2081, 2083, 2087, 2089, 2099, 2111, 2113, 2129, 2131, 2137, 2141, 2143, 2153, 2161, 2179, 2203, 2207, 2213, 2221, 2237, 2239, 2243, 2251, 2267, 2269, 2273, 2281, 2287, 2293, 2297, 2309, 2311, 2333, 2339, 2341, 2347, 2351, 2357, 2371, 2377, 2381, 2383, 2389, 2393, 2399, 2411, 2417, 2423, 2437, 2441, 2447, 2459, 2467, 2473, 2477, 2503, 2521, 2531, 2539, 2543, 2549, 2551, 2557, 2579, 2591, 2593, 2609, 2617, 2621, 2633, 2647, 2657, 2659, 2663, 2671, 2677, 2683, 2687, 2689, 2693, 2699, 2707, 2711, 2713, 2719, 2729, 2731, 2741, 2749, 2753, 2767, 2777, 2789, 2791, 2797, 2801, 2803, 2819, 2833, 2837, 2843, 2851, 2857, 2861, 2879, 2887, 2897, 2903, 2909, 2917, 2927, 2939, 2953, 2957, 2963, 2969, 2971, 2999, 3001, 3011, 3019, 3023, 3037, 3041, 3049, 3061, 3067, 3079, 3083, 3089, 3109, 3119, 3121, 3137, 3163, 3167, 3169, 3181, 3187, 3191, 3203, 3209, 3217, 3221, 3229, 3251, 3253, 3257, 3259, 3271, 3299, 3301, 3307, 3313, 3319, 3323, 3329, 3331, 3343, 3347, 3359, 3361, 3371, 3373, 3389, 3391, 3407, 3413, 3433, 3449, 3457, 3461, 3463, 3467, 3469, 3491, 3499, 3511, 3517, 3527, 3529, 3533, 3539, 3541, 3547, 3557, 3559, 3571, 3581, 3583, 3593, 3607, 3613, 3617, 3623, 3631, 3637, 3643, 3659, 3671, 3673, 3677, 3691, 3697, 3701, 3709, 3719, 3727, 3733, 3739, 3761, 3767, 3769, 3779, 3793, 3797, 3803, 3821, 3823, 3833, 3847, 3851, 3853, 3863, 3877, 3881, 3889, 3907, 3911, 3917, 3919, 3923, 3929, 3931, 3943, 3947, 3967, 3989, 4001, 4003, 4007, 4013, 4019, 4021, 4027, 4049, 4051, 4057, 4073, 4079, 4091, 4093, 4099, 4111, 4127, 4129, 4133, 4139, 4153, 4157, 4159, 4177, 4201, 4211, 4217, 4219, 4229, 4231, 4241, 4243, 4253, 4259, 4261, 4271, 4273, 4283, 4289, 4297, 4327, 4337, 4339, 4349, 4357, 4363, 4373, 4391, 4397, 4409, 4421, 4423, 4441, 4447, 4451, 4457, 4463, 4481, 4483, 4493, 4507, 4513, 4517, 4519, 4523, 4547, 4549, 4561, 4567, 4583, 4591, 4597, 4603, 4621, 4637, 4639, 4643, 4649, 4651, 4657, 4663, 4673, 4679, 4691, 4703, 4721, 4723, 4729, 4733, 4751, 4759, 4783, 4787, 4789, 4793, 4799, 4801, 4813, 4817, 4831, 4861, 4871, 4877, 4889, 4903, 4909, 4919, 4931, 4933, 4937, 4943, 4951, 4957, 4967, 4969, 4973, 4987, 4993, 4999, 5003, 5009, 5011, 5021, 5023, 5039, 5051, 5059, 5077, 5081, 5087, 5099, 5101, 5107, 5113, 5119, 5147, 5153, 5167, 5171, 5179, 5189, 5197, 5209, 5227, 5231, 5233, 5237, 5261, 5273, 5279, 5281, 5297, 5303, 5309, 5323, 5333, 5347, 5351, 5381, 5387, 5393, 5399, 5407, 5413, 5417, 5419, 5431, 5437, 5441, 5443, 5449, 5471, 5477, 5479, 5483, 5501, 5503, 5507, 5519, 5521, 5527, 5531, 5557, 5563, 5569, 5573, 5581, 5591, 5623, 5639, 5641, 5647, 5651, 5653, 5657, 5659, 5669, 5683, 5689, 5693, 5701, 5711, 5717, 5737, 5741, 5743, 5749, 5779, 5783, 5791, 5801, 5807, 5813, 5821, 5827, 5839, 5843, 5849, 5851, 5857, 5861, 5867, 5869, 5879, 5881, 5897, 5903, 5923, 5927, 5939, 5953, 5981, 5987, 6007, 6011, 6029, 6037, 6043, 6047, 6053, 6067, 6073, 6079, 6089, 6091, 6101, 6113, 6121, 6131, 6133, 6143, 6151, 6163, 6173, 6197, 6199, 6203, 6211, 6217, 6221, 6229, 6247, 6257, 6263, 6269, 6271, 6277, 6287, 6299, 6301, 6311, 6317, 6323, 6329, 6337, 6343, 6353, 6359, 6361, 6367, 6373, 6379, 6389, 6397, 6421, 6427, 6449, 6451, 6469, 6473, 6481, 6491, 6521, 6529, 6547, 6551, 6553, 6563, 6569, 6571, 6577, 6581, 6599, 6607, 6619, 6637, 6653, 6659, 6661, 6673, 6679, 6689, 6691, 6701, 6703, 6709, 6719, 6733, 6737, 6761, 6763, 6779, 6781, 6791, 6793, 6803, 6823, 6827, 6829, 6833, 6841, 6857, 6863, 6869, 6871, 6883, 6899, 6907, 6911, 6917, 6947, 6949, 6959, 6961, 6967, 6971, 6977, 6983, 6991, 6997, 7001, 7013, 7019, 7027, 7039, 7043, 7057, 7069, 7079, 7103, 7109, 7121, 7127, 7129, 7151, 7159, 7177, 7187, 7193, 7207, 7211, 7213, 7219, 7229, 7237, 7243, 7247, 7253, 7283, 7297, 7307, 7309, 7321, 7331, 7333, 7349, 7351, 7369, 7393, 7411, 7417, 7433, 7451, 7457, 7459, 7477, 7481, 7487, 7489, 7499, 7507, 7517, 7523, 7529, 7537, 7541, 7547, 7549, 7559, 7561, 7573, 7577, 7583, 7589, 7591, 7603, 7607, 7621, 7639, 7643, 7649, 7669, 7673, 7681, 7687, 7691, 7699, 7703, 7717, 7723, 7727, 7741, 7753, 7757, 7759, 7789, 7793, 7817, 7823, 7829, 7841, 7853, 7867, 7873, 7877, 7879, 7883, 7901, 7907, 7919]
def is_prime(number):
    return is_int(number) and number > 1 and number in PRIME_NUMBERS

FACTORS_ALL = 'all'
FACTORS_PROPER = 'proper'
FACTORS_PRIME = 'prime'
def factors(n, form=FACTORS_PROPER):
    if form == FACTORS_PRIME:
        primes = []
        i = 2
        while n % i == 0:
            primes.append(i)
            n /= i
        i = 3
        while n > 1:
            while n % i == 0:
                primes.append(i)
                n /= i
            i += 2
        return primes
    else:
        all_factors = reduce(list.__add__, ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0))
        if form == FACTORS_PROPER:
            all_factors.remove(n)
        return all_factors


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

def is_close(num1, num2, threshold=1e-5, method='raw'):
    if isinstance(num1, ComputationError) or isinstance(num2, ComputationError):
        return False
    elif hasattr(num1, '__iter__'):
        return any(is_close(n, num2, threshold) for n in num1)
    elif hasattr(num2, '__iter__'):
        return any(is_close(num1, n, threshold) for n in num2)
    elif (isinstance(num1, complex) or isinstance(num2, complex)) and type(num1) != type(num2):
        return False
    else:
        if method == 'pct':
            return abs(num1-num2) / max(num1, num2) < threshold
        else:
            return abs(num1-num2) < threshold

def to_ordinal(n):
    str_n = str(n)
    ones = n % 10
    if 1 <= ones <= 3 and n not in (11, 12, 13):
        if ones == 1:
            return str_n + 'st'
        elif ones == 2:
            return str_n + 'nd'
        else:
            return str_n + 'rd'
    else:
        return str_n + 'th'

def to_pretty_x10(n, dec_places=5, prepend='', append=''):
    if n < sys.float_info.min or n > sys.float_info.max:
        val = decimal.Decimal(n)
        decimal.getcontext().prec = dec_places+1
        val = str(val.normalize())
    elif not is_int(n) or math.log10(n) > 10:
        val = ('%0.'+str(dec_places+1)+'G') % n
        v = val.split('E')
        if len(v) == 1:
            left = v[0].split('.')
            if len(left) > 1 and len(left[1]) > dec_places:
                left[1] = left[1][:dec_places]
            val = '.'.join(left)
    else:
        val = str(n)
    val = val.split('E')

    if len(val) == 1:
        return prepend + val[0] + append
    else:
        if val[1].startswith('+'):
            val[1] = str(int(val[1][1:]))
        return prepend + val[0] + '×10^' + val[1] + append


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
