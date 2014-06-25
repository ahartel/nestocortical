import sys
import numpy as np
import matplotlib.pyplot as plt

num_files = len(sys.argv)-1
max_times = []
min_neuron_number = 0
max_neuron_number = 0
spikes = {}

for i,f in enumerate(sys.argv[1:]):
    print "processing file "+f
    data = np.loadtxt(f,delimiter='\t')
    for d in data:
        try:
            spikes[d[0]].append(d[1])
        except KeyError:
            spikes[d[0]] = []
        except IndexError:
            break

    for n,sp in spikes.items():
        plt.plot(sp,np.ones(len(sp))*n,'bo')

    max_times.append(np.max(sp))
    #try:
    #    times = data[:,1]
    #    max_times[i] = np.max(times)
    #    spikes = data[:,0]
    #    min_neuron_number = np.min(spikes[0])
    #    max_neuron_number = np.max(spikes[0])
    #    plt.plot(times,spikes,'o')
    #except IndexError:
    #    pass

for x in range(0,int(max(max_times))+1,50):
    plt.axvline(x)

plt.xlim(0,np.max(max_times))
#plt.ylim(min_neuron_number-1,max_neuron_number+1)
plt.show()
