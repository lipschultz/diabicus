from matplotlib import pyplot
from decimal import Decimal as D

with open('int_counts-Numberphile.tab') as fin:
    data = [line.strip().split('\t') for line in fin]

data = data[1:]
data = [(D(v[0]), int(v[1])) for v in data]

x = [v[0] for v in data]
y = [v[1] for v in data]

#x = x[:200]
#y = y[:200]
c = ['red' if (v % 1).is_zero() else 'blue' for v in x]
pyplot.scatter(x, y, s=1, color=c)
pyplot.show()
