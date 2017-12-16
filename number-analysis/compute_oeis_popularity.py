import gzip
import sqlite3


def get_counts(conn, oeis_filename):
    c = conn.cursor()
    with gzip.open(oeis_filename, 'rb') as fin:
        for line in fin:
            if line.startswith(b'#'):
                continue

            label, *values = [v.strip() for v in line.split(b',')]

            link = 'http://oeis.org/' + str(label)
            source = 'OEIS'
            c.execute('INSERT INTO videos(link, title, source) VALUES (?, ?, ?)', (link, label, source))
            video_id = c.lastrowid
            for value in values:
                if len(value) > 0:
                    value = int(value)
                    try:
                        c.execute('INSERT INTO counts(video_id, real_part, imag_part) VALUES (?, ?, ?)', (video_id, value, 0))
                    except OverflowError as e:
                        c.execute('INSERT INTO counts(video_id, real_part, imag_part) VALUES (?, ?, ?)', (video_id, str(value), 0))
    conn.commit()


if __name__ == '__main__':
    oeis_file = 'data/oeis.gz'
    db_file = 'data/data-real,imag.db'
    conn = sqlite3.connect(db_file)
    get_counts(conn, oeis_file)
    conn.close()
