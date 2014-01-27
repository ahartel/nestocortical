import numpy as np
import matplotlib.pyplot as plt
from wta import num

file_stem = './Results/wta_np1_nest_'
spikes = [None] * (num['inputs']+num['nodes']*num['exc_neurons']+num['inh_neurons'])
offset = num['inputs']

color_input = 'red'
color_exc = 'green'
color_inh = 'blue'

for i in range(num['inputs']):
	spikes[i] = np.loadtxt(file_stem+'input_'+str(i)+'.ras',usecols=(0,))
	plt.plot(spikes[i],np.ones(len(spikes[i]))*i,linestyle='',marker='|',color=color_input)

plt.axhline(y=offset)

for i in range(num['nodes']):
	for j in range(num['exc_neurons']):
		spikes[offset+j] = []
	#spikes.append(np.loadtxt(file_stem+'output_'+str(i)+'.ras',usecols=(0,),ndmin=1))
	this_spikes = np.loadtxt(file_stem+'output_'+str(i)+'.ras',usecols=(0,1),ndmin=2)
	for spike in this_spikes:	
		spikes[offset+int(spike[1])].append(spike[0])
	for j in range(num['exc_neurons']):
		plt.plot(spikes[offset+j],np.ones(len(spikes[offset+j]))*(offset+j),linestyle='',marker='|',color=color_exc)

	offset += num['exc_neurons']

plt.axhline(y=offset)

# inhibitory
this_spikes = np.loadtxt(file_stem+'inhibit.ras',usecols=(0,1),ndmin=1)
for j in range(num['inh_neurons']):
	spikes[offset+j] = []
for spike in this_spikes:
	spikes[offset+int(spike[1])].append(spike[0])
for j in range(num['inh_neurons']):
	plt.plot(spikes[offset+j],np.ones(len(spikes[offset+j]))*(offset+j),linestyle='',marker='|',color=color_inh)

		
plt.show()
