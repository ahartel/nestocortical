import sys,pickle
import xnet
import numpy as np
import matplotlib.pyplot as plt

dvs = xnet.DVSLoader(sys.argv[1])

image_width = 128
image_height = 128
num_neurons_first  = 60
num_neurons_second = 10
num_dvs_addresses = 2 * image_width * image_height

neurons_first  = xnet.Neurons(num_neurons_first)

synapses = [[xnet.Synapse(i*num_dvs_addresses+j,neurons_first,j) for j in range(num_neurons_first)] for i in range(num_dvs_addresses)]

#cnt = 0
for event in dvs.get_events():
	#if cnt == 1000000:
	#	break

	time = event[0]
	for synapse in synapses[event[1]]:
		synapse.pre(time)
	#cnt += 1

spikes = neurons_first.get_spikes()
pickle.dump(spikes,open('spikes.dat','wb'))

for n in range(num_neurons_first):
	#if len(spikes[n]) > 0:
	#	print n,len(spikes[n])
	plt.plot(spikes[n],np.ones(len(spikes[n]))*n,'o')

plt.show()

