import sys
import numpy as np
import matplotlib.pyplot as plt


for i,f in enumerate(sys.argv[1:]):
    plt.figure()
    data = np.loadtxt(f)
    traces = len(data[0])-2
    times = data[:,1]
    for i in range(traces):
        plt.subplot(traces*100+10+i+1)
        plt.plot(times,data[:,i+2])

plt.show()
