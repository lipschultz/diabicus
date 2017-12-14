import atexit
import sqlite3
import sys

from collections import namedtuple
from datetime import datetime
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
        c.execute('CREATE TABLE videos (video_id INTEGER PRIMARY KEY, link TEXT, date TEXT, title TEXT, source TEXT)')
        c.execute('CREATE TABLE hosts (video_id INTEGER, host TEXT, FOREIGN KEY(video_id) REFERENCES videos(video_id))')
        c.execute('CREATE TABLE counts (video_id INTEGER, real_part NUMERIC, imag_part NUMERIC, FOREIGN KEY(video_id) REFERENCES videos(video_id))')
        conn.commit()

    return conn


def add_facts_to_db(facts, conn):
    link_id_map = {}
    c = conn.cursor()
    for f in facts:
        c.execute('SELECT video_id FROM videos WHERE link=?', (f.link, ))
        row = c.fetchone()
        if row is None:
            c.execute('INSERT INTO videos(link, date, title, source) VALUES (?, ?, ?, ?)', (f.link, f.date, f.title, f.source))
            link_id_map[f.link] = c.lastrowid
            for h in f.host:
                c.execute('INSERT INTO hosts VALUES (?, ?)', (link_id_map[f.link], h))
        else:
            link_id_map[f.link] = row[0]
    conn.commit()
    return link_id_map


def drange(start, end, step="1"):
    start = Decimal(start)
    end = Decimal(end)
    step = Decimal(step)
    while start < end:
        yield start
        start += step


def get_counts(conn, facts, link_id_map, real_start, real_end, real_step=1):
    cursor = conn.cursor()
    start_time = datetime.now()
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
        if num_count % 1e3 == 0:
            time_diff = datetime.now() - start_time
            rate = num_count / time_diff.total_seconds()
            real_total = (real_end - real_start) / float(real_step)
            imag_total = 1
            num_total = real_total * imag_total
            num_remaining = num_total - num_count
            est_time_remaining = num_remaining / rate / 3600
            print('{num}: {count}, {time}; rate={rate:0.2f}, ETR={etr:0.2f}h'.format(num=num, count=num_count, time=time_diff, rate=rate, etr=est_time_remaining))
            #print(real, num_count, time_diff, (num_count / time_diff.total_seconds()))

        count_data = []
        links_matched = set()
        for f in facts:
            if f.link not in links_matched and f.test(str(num), num, {'result' : [num], 'formula' : [str(num)]}):
                count_data.append(FactNumberMatch(link_id_map[f.link], real, imag))
                links_matched.add(f.link)
        cursor.executemany('INSERT INTO counts VALUES (?, ?, ?)', count_data)
        conn.commit()


if __name__ == '__main__':
    facts = load_tests()
    conn = get_database('data.db')
    link_id_map = add_facts_to_db(facts, conn)
    get_counts(conn, facts, link_id_map, -10000, 10001, '0.01')
    conn.close()
