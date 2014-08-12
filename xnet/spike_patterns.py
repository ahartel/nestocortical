import sys,pickle
import numpy as np
import matplotlib.pyplot as plt

num_repetitions = 100

spikes = pickle.load(open(sys.argv[1]))
bins = np.linspace(0,8*num_repetitions*100,8*num_repetitions+1)
times = {}

for n,neuron_spikes in enumerate(spikes):
	digitized = np.digitize(neuron_spikes, bins)
	for bin in digitized:
		try:
			times[bin].append(n)
		except KeyError:
			times[bin] = [n]

for angle in range(1,17,2):
	print 'angle ',angle
	for i in range(angle,8*num_repetitions,16):
		try:
			print i,times[i]
		except KeyError:
			pass

for n in range(48):
	plt.plot(spikes[n],n*np.ones(len(spikes[n])),'o')

for n in range(num_repetitions*8*2):
	plt.axvline(n*100)

plt.show()
