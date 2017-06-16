from collections import OrderedDict
from matplotlib import pyplot

int_counts = {}
sequence_count = 0
with open('stripped') as fin:
    for line in fin:
        if line.startswith('#'):
            continue

        line = line.split(',')
        ano = line[0]
        line = line[1:]
        line = [int(l.strip()) for l in line if len(l.strip()) > 0]
        
        for i in line:
            int_counts[i] = int_counts.get(i, 0) + 1

        sequence_count += 1

print('sequence_count:', sequence_count)

int_counts = OrderedDict(sorted(int_counts.items(), key=lambda t: t[0]))

with open('oeis-int_counts.tab', 'w') as fout:
    fout.write('int\tcount\n')
    for i, c in int_counts.items():
        fout.write('%d\t%d\n' % (i, c))

x = list(int_counts.keys())
y = list(int_counts.values())
y = [float(v)/sequence_count for v in y]
pyplot.scatter(x, y, s=1, color='blue')
pyplot.xlim(1,10000)
pyplot.yscale('log')
pyplot.show()
