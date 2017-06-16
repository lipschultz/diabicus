import math
import statistics
import sys
from decimal import Decimal as D

sys.path.append('..')
from src import numeric_tools

SOURCE_COUNT = {'oeis' : 285638,
                'Numberphile' : 323,
                'standupmaths' : 76
               }

def load_int_counts(filename):
    with open(filename) as fin:
        data = [line.strip().split('\t') for line in fin]
        data = data[1:] # header
        data = dict((D(v[0]), int(v[1])) for v in data)
        return data

def keep_only_within_range(counts, min_value, max_value):
    return dict([(i, c) for i, c in counts.items() if min_value <= i <= max_value])

def is_integer(d):
    return numeric_tools.is_int(d) or (d % 1) == 0

def keep_only_ints(counts):
    return dict([(int(i), c) for i, c in counts.items() if is_integer(i)])

def write_analysis(filename, **data):
    keys = list(data.keys())
    keys.sort()
    headers = ['int'] + [k for k in data]
    print('using header:', headers[1])
    nums = list(data[headers[1]].keys())
    nums.sort()
    with open(filename, 'w') as fout:
        fout.write('\t'.join(headers) + '\n')
        for i in nums:
            fout.write(str(i) + '\t')
            ovals = []
            for h in keys:
                try:
                    ovals.append(str(data[h][i]))
                except KeyError:
                    print(i, h)
                    with open('/tmp/a.csv', 'w') as tf:
                        tf.write(str(data[h]))
                        raise Exception
            
            #fout.write('\t'.join([str(data[h][i]) for h in headers[1:]]))
            fout.write('\t'.join(ovals))
            fout.write('\n')

def tag_as_frequent_Numberphile(num, count):
    num = float(num)
    if num < 85:
        return 1 if count > 34 else 0
    elif num < 250:
        #(25, 43) -> (250, 31)
        #(x1, y1) -> (x2, y2)
        x1, y1 = 85, 34
        x2, y2 = 250, 31
        return 1 if count > ((y2-y1)/(x2-x1)*num + (y1 - (y2-y1)/(x2-x1)*x1)) else 0
    else:
        return 1 if count > 30 else 0

def tag_as_frequent_standupmaths(int_val, count):
    return 0

TAG_AS_FREQ_FN = {'Numberphile' : tag_as_frequent_Numberphile,
                  'standupmaths' : tag_as_frequent_standupmaths
                 }

MAX_PRIME = max(numeric_tools.PRIME_NUMBERS)

def label_data(data, oeis, source):
    avg = statistics.mean([v for v in data.values()])
    std = statistics.stdev([v for v in data.values()])

    q2 = median = statistics.median([v for v in data.values()])

    lower = [v for v in data.values() if v < median]
    if len(lower) == 0:
        q1 = 0
    else:
        q1 = statistics.median(lower)
    q3 = statistics.median([v for v in data.values() if v >= median])
    iqr = q3-q1

    oeis_ratio_raw = {} #probability of popularity in data given popularity in oeis
    oeis_ratio_pct = {} #probability of popularity in data given popularity in oeis
    is_interesting = {}
    is_square = {} #3.3.1
    is_prime = {} #3.3.2
    num_factors = {} #3.3.3
    is_frequent = {}
    zscore = {}
    is_tukey_outlier = {}
    counts_pct = {}
    oeis_pct = {}
    is_int = {}
    for i, c in data.items():
        if i in oeis:
            oeis_ratio_raw[i] = c / oeis[i]
            oeis_ratio_pct[i] = (c/SOURCE_COUNT[source]) / (oeis[i]/SOURCE_COUNT['oeis'])
            oeis_pct[i] = oeis[i] / SOURCE_COUNT['oeis']
        else:
            oeis_ratio_raw[i] = ''
            oeis_ratio_pct[i] = ''
            oeis_pct[i] = ''
            oeis[i] = ''

        counts_pct[i] = c / SOURCE_COUNT[source]

        if is_integer(i):
            ii = int(i)
            is_int[i] = 1
            is_square[i] = 1 if is_integer(math.sqrt(i)) else 0
            num_factors[i] = len(numeric_tools.factors(ii, numeric_tools.FACTORS_PRIME))

            if numeric_tools.is_prime(ii):
                is_prime[i] = 1
            elif MAX_PRIME < i:
                is_prime[i] = ''
            else:
                is_prime[i] = 0

        else:
            is_int[i] = 0
            is_square[i] = 0
            num_factors[i] = 0
            is_prime[i] = 0
            
        is_interesting[i] = 1 if i-1 in data and c > data[i-1] else 0
        zscore[i] = (c - avg)/std
        is_tukey_outlier[i] = 0 if q1-1.5*iqr <= c <= q3+1.5*iqr else 1
        is_frequent[i] = TAG_AS_FREQ_FN[source](i, c)

    write_analysis('analysis-'+source+'.tab', counts=data, oeis=oeis,
                   counts_pct=counts_pct, oeis_pct=oeis_pct,
                   oeis_ratio_raw=oeis_ratio_raw, oeis_ratio_pct=oeis_ratio_pct,
                   is_interesting=is_interesting, is_square=is_square,
                   is_prime=is_prime, num_factors=num_factors, zscore=zscore,
                   is_tukey_outlier=is_tukey_outlier, is_frequent=is_frequent,
                   is_int=is_int
                  )

if __name__ == '__main__':
    source = 'Numberphile'
    oeis = load_int_counts('oeis-int_counts.tab')
    data = load_int_counts('../int_counts-'+source+'.tab')

    oeis = keep_only_within_range(oeis, 1, 10000)
    data = keep_only_within_range(data, 1, 10000)
    #data = keep_only_ints(data)

    label_data(data, oeis, source)
