import atexit
import sqlite3
import sys
import time

from collections import namedtuple
from decimal import Decimal
from os.path import exists, abspath, join

import numpy as np
import pandas as pd

sys.path.insert(0, abspath('..'))
from resources import youtube_facts


FactNumberMatch = namedtuple('FactNumberMatch', ('link', 'real', 'imag'))


def load_tests(source=None):
    facts = youtube_facts.load_facts()
    facts = facts.cases
    if source is None:
        return facts
    else:
        return [f for f in facts if f.source == source]


def get_database(path):
    create_db = not exists(path)
    conn = sqlite3.connect(path)
    c = conn.cursor()

    if create_db:
        c.execute('CREATE TABLE videos (link text, date text, title text, source text)')
        c.execute('CREATE TABLE hosts (link text, host text, FOREIGN KEY(link) REFERENCES videos(link))')
        c.execute('CREATE TABLE counts (link text, real_part numeric, imag_part numeric, FOREIGN KEY(link) REFERENCES videos(link))')
        conn.commit()

    return conn


def add_facts_to_db(facts, conn):
    c = conn.cursor()
    for f in facts:
        print(f.link)
        c.execute('SELECT link FROM videos WHERE link=?', (f.link, ))
        res = c.fetchone()
        if res is None:
            print('adding', f.link)
            c.execute('INSERT INTO videos VALUES (?, ?, ?, ?)', (f.link, f.date, f.title, f.source))
            for h in f.host:
                c.execute('INSERT INTO hosts VALUES (?, ?)', (f.link, h))
    conn.commit()


def drange(start, end, step="1"):
    start = Decimal(start)
    end = Decimal(end)
    step = Decimal(step)
    while start < end:
        yield start
        start += step


def get_counts(conn, facts, real_start, real_end, real_step=1):
    cursor = conn.cursor()
    start_time = time.time()
    print('start', 0, 0)
    if isinstance(real_step, int):
        real_vals = range(real_start, real_end, real_step)
    elif isinstance(real_step, float):
        real_vals = np.arange(real_start, real_end, real_step)
    elif isinstance(real_step, str):
        real_vals = drange(real_start, real_end, real_step)

    imag = 0
    num_count = 0
    for real in real_vals:
        real = int(real) if (real % 1).is_zero() else float(real)

        num = real
        if imag != 0:
            num += complex(0, imag)

        num_count += 1
        if num_count % 1e6 == 0:
            print(real, num_count, time.time() - start_time)

        count_data = []
        links_matched = set()
        for f in facts:
            print(f.link)
            if f.link not in links_matched and f.test(str(num), num, {'result' : [num], 'formula' : [str(num)]}):
                count_data.append(FactNumberMatch(f.link, real, imag))
                links_matched.add(f.link)
        cursor.executemany('INSERT INTO counts VALUES (?, ?, ?)', count_data)
        conn.commit()


if __name__ == '__main__':
    facts = load_tests()
    print(facts)
    conn = get_database('data.db')
    add_facts_to_db(facts, conn)
    get_counts(conn, facts, -10000, 10001, '0.01')
    conn.close()
