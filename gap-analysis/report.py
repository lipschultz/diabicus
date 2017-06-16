import pandas as pd
from matplotlib import pyplot

source = 'standupmaths'

df = pd.read_csv('analysis-'+source+'.dat', sep='\t')

df.plot.scatter(x='int', y='counts', s=1, c=['red' if v == 1 else 'blue' for v in df['is_frequent']])

pyplot.show()
