import sys
from nest import *
import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt(sys.argv[1])

traces = len(data[0])-2
times = data[:,1]
for i in range(traces):
    plt.subplot(traces*100+10+i+1)
    plt.plot(times,data[:,i+2])

plt.show()
