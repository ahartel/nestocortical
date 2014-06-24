import sys
import numpy as np
import matplotlib.pyplot as plt

num_files = len(sys.argv)-1
max_times = np.zeros(num_files)
neuron_numbers = np.zeros(num_files)

for i,f in enumerate(sys.argv[1:]):
    print "processing file "+f
    data = np.loadtxt(f)
    times = data[:,1]
    max_times[i] = np.max(times)
    spikes = data[:,0]
    neuron_numbers[i] = spikes[0]
    plt.plot(times,spikes,'o')

for x in range(0,int(max(max_times))+1,50):
    plt.axvline(x)

plt.xlim(0,np.max(max_times))
plt.ylim(np.min(neuron_numbers)-1,np.max(neuron_numbers)+1)
plt.show()
