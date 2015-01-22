import sys
import numpy as np
import matplotlib.pyplot as plt

binning = 0.01

data = np.loadtxt(sys.argv[1],delimiter=',',ndmin=2)

ax1 = plt.subplot(211)
plt.plot(data[:,1],data[:,0],'o')
plt.grid()
plt.subplot(212, sharex=ax1)
bins = np.arange(int(data[0][1]*1000.0),int(data[-1][1]*1000.0),int(binning*1000.0))
hist,bin_edges = np.histogram(data[:,1]*1000,bins=bins)
plt.plot(bins[1:]/1000.0,hist/binning)
plt.grid()

plt.show()
