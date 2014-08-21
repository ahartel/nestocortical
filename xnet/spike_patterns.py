import sys
import numpy as np
import matplotlib.pyplot as plt

num_repetitions = 100

data = np.loadtxt(sys.argv[1],delimiter=',')
bins = np.linspace(0,8*num_repetitions*100,8*num_repetitions+1)
times = {}

spikes = [[] for n in range(48)]
for sp in data:
    spikes[int(sp[0])].append(sp[1])

for n,neuron_spikes in enumerate(spikes):
    try:
        digitized = np.digitize(neuron_spikes, bins)
        for bin in digitized:
            try:
                times[bin].append(n)
            except KeyError:
                times[bin] = [n]
    except ValueError:
        print "No spikes for neuron ",n

for angle in range(1,17,2):
	print 'angle ',angle/2
	for i in range(angle,8*num_repetitions,16):
		try:
			print i,times[i]
		except KeyError:
			pass

