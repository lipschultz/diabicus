import sys
import time
import atexit
from os.path import exists, abspath, join
from collections import OrderedDict
from decimal import Decimal

import numpy as np
#from matplotlib import pyplot

sys.path.insert(0, abspath('..'))
from resources import youtube_facts

def drange(start, end, step="1"):
    start = Decimal(start)
    end = Decimal(end)
    step = Decimal(step)
    while start < end:
        yield start
        start += step

def load_tests(source=None):
    facts = youtube_facts.load_facts()
    facts = facts.cases
    return [f for f in facts if source is not None and f.source == source]

def get_last_int_done(filename):
    if not exists(filename):
        return None
    with open(filename) as fin:
        fin.readline() #header
        return max(float(l.split('\t')[0]) for l in fin)
            
def save_info():
    file_exists = exists(int_counts_filename)
    with open(int_counts_filename, 'a') as fout:
        if not file_exists:
            fout.write('int\tcount\n')
        for i, c in int_counts.items():
            fout.write('%s\t%d\n' % (str(i), c))

    filename = 'video_counts-'+source+'.tab'
    file_exists = exists(filename)
    with open(filename, 'a') as fout:
        if not file_exists:
            fout.write('title\tlink\tcount\n')
        for link, count in video_counts.items():
            fout.write('%s\t%s\t%d\n' % (link_to_title[link], link, count))

def get_counts(facts, start, end, step=1):
    global int_counts
    global video_counts
    int_counts = OrderedDict()
    video_counts = dict(zip([f.link for f in facts], [0 for f in facts]))
    start_time = time.time()
    print('start', 0, 0)
    if isinstance(step, int):
        range_vals = range(start, end)
    elif isinstance(step, float):
        range_vals = np.arange(start, end, step)
    elif isinstance(step, str):
        range_vals = drange(start, end, step)
        
    for i in range_vals:
        if len(int_counts) % 1e6 == 0:
            print(i, len(int_counts), time.time() - start_time)
        count = 0
        links_matched = set()
        num = int(i) if (i % 1).is_zero() else float(i)
        for f in facts:
            if f.link not in links_matched and f.test(str(num), num, {'result' : [num], 'formula' : [str(num)]}):
                count += 1
                links_matched.add(f.link)
                video_counts[f.link] = video_counts.get(f.link, 0) + 1
        int_counts[i] = count
    return int_counts, video_counts

'''
x = list(int_counts.keys())
y = list(int_counts.values())
#y = [v/len(link_to_title) for v in y]
pyplot.scatter(x, y, s=1, color='red')
#pyplot.xlim(1,10000)
pyplot.xlim(1,1000)
#pyplot.yscale('log')
pyplot.show()
'''

if __name__ == '__main__':
    source = 'Numberphile'
    #source = 'standupmaths'
    int_counts_filename = 'int_counts-'+source+'.tab'
    facts = load_tests(source)
    link_to_title = dict([(f.link, f.title) for f in facts])
    print('video count:', len(link_to_title))

    last_int = get_last_int_done(int_counts_filename)
    last_int = -2**32 if last_int is None else last_int
    print('Starting at', last_int)
    last_int = -10000
    print('Resetting to start at', last_int)

    atexit.register(save_info)

    get_counts(facts, last_int, 10001, "0.01")
