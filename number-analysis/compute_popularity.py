import random
import sqlite3
import sys
import time

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


class Range:
    def __init__(self, start, end, step=1, imag=False):
        self.start = start
        self.end = end
        self.step = step
        self.imag = imag

    def create_range(self):
        if isinstance(self.step, int):
            r = range(self.start, self.end, self.step)
        elif isinstance(self.step, float):
            r = np.arange(self.start, self.end, self.step)
        elif isinstance(self.step, str):
            r = self.__drange(self.start, self.end, self.step)
        if self.imag:
            r = self.__make_imaginary(r)
        return r

    def __len__(self):
        return int((self.end - self.start) / float(self.step))

    def __drange(self, start, end, step="1"):
        start = Decimal(start)
        end = Decimal(end)
        step = Decimal(step)
        while start < end:
            start_val = int(start) if (start % 1).is_zero() else float(start)
            yield start_val
            start += step

    def __make_imaginary(self, range_generator):
        for val in range_generator:
            yield val * 1j


def get_counts(conn, facts, link_id_map, real_range, imag_range, skip_fn=None, resume_after=None):
    cursor = conn.cursor()
    start_time = datetime.now()
    print('start', 0, 0)

    num_total = len(real_range) * len(imag_range)
    num_count = 0
    count_data = []
    confirm_commit = False
    for real in real_range.create_range():
        if resume_after is not None and real < resume_after[0]:
            num_total -= len(imag_range)
            continue

        for imag in imag_range.create_range():
            if resume_after is not None and real == resume_after[0] and imag <= resume_after[1]:
                num_total -= 1
                continue

            num_count += 1

            num = real
            if imag != 0:
                num += complex(0, imag)

            if num_count % 1e3 == 0:
                time_diff = datetime.now() - start_time
                rate = num_count / time_diff.total_seconds()
                num_remaining = num_total - num_count
                est_time_remaining = num_remaining / rate / 3600
                print('{num}: {count}/{total}, {time}; rate={rate:0.2f}, ETR={etr:0.2f}h'.format(num=num, count=num_count, total=num_total, time=time_diff, rate=rate, etr=est_time_remaining))
                if confirm_commit:
                    input("Commit this? Ctrl-C if no")
                    confirm_commit = False

                for failure_count in range(3):
                    try:
                        cursor.executemany('INSERT INTO counts VALUES (?, ?, ?)', count_data)
                        conn.commit()
                        break
                    except sqlite3.OperationalError as e:
                        print('Failed to insert:', e)
                        if failure_count == 2:
                            raise e
                        else:
                            time.sleep(2*random.random())

                count_data = []
                #print(real, num_count, time_diff, (num_count / time_diff.total_seconds()))

            if skip_fn is not None and skip_fn(real, imag):
                continue

            links_matched = set()
            for f in facts:
                if f.link not in links_matched and f.test(str(num), num, {'result' : [num], 'formula' : [str(num)]}):
                    count_data.append(FactNumberMatch(link_id_map[f.link], real, imag))
                    links_matched.add(f.link)


if __name__ == '__main__':
    facts = load_tests()
    conn = get_database('data.db')
    link_id_map = add_facts_to_db(facts, conn)

    ideal_min = -10000
    ideal_max = 10001
    ideal_step = '0.01'
    resume_after = None

    # real_range = Range(0, ideal_max, 1)
    # imag_range = Range(0, ideal_max, 1)
    # resume_after = (7311, 1688)

    # real_range = Range(ideal_min, 0, 1)
    # imag_range = Range(0, ideal_max, 1)
    # resume_after = (-2816, 2815)
    # TODO: skipped this range:
    #       (-5189+2188j): 48117000/100010000, 1 day, 19:20:01.751491; rate=308.44, ETR=46.73h
    #       (-5189+3188j)

    # real_range = Range(0, ideal_max, 1)
    # imag_range = Range(ideal_min, 0, 1)
    # resume_after = (7217, -8001)
    # TODO: skipped this range:
    #       (4838-1001j): 48389000/100010000, 1 day, 19:18:55.840213; rate=310.31, ETR=46.21h
    #       (4838-1j): 48390000/100010000, 1 day, 19:19:01.104841; rate=310.31, ETR=46.21h

    real_range = Range(ideal_min, 0, 1)
    imag_range = Range(ideal_min, 0, 1)
    resume_after = (-2304, -3001)

    skip_fn = lambda r, i: r == 0 or i == 0
    get_counts(conn, facts, link_id_map, real_range, imag_range, skip_fn, resume_after)
    conn.close()
