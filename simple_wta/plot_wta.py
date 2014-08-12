import numpy as np
import matplotlib.pyplot as plt
from wta import num

file_stem = './Results/wta_np1_nest_'
#spikes = [None] * (num['inputs']+num['nodes']*num['exc_neurons']+num['inh_neurons'])
#offset = num['inputs']

color_input = 'red'
color_exc = 'green'
color_inh = 'blue'

skiprows = 0

def plot_section(offset,num,file_leaf,color):
    spikes = [None] * num
    for j in range(num):
        spikes[j] = []
    this_spikes = np.loadtxt(file_stem+file_leaf+'.ras',usecols=(0,1),ndmin=2,skiprows=skiprows)
    for spike in this_spikes:
        spikes[int(spike[1])].append(spike[0])
    for j in range(num):
        plt.plot(spikes[j],np.ones(len(spikes[j]))*(offset+j),linestyle='',marker='|',color=color)

offset = 0
for i in range(num['bump_max_neighbor']*4):
    plot_section(offset,num['stims_per_neuron'],'input_'+str(i),color_input)
    offset += num['stims_per_neuron']

plt.axhline(y=offset)
plot_section(offset,num['exc_neurons'],'output',color_exc)
offset += num['exc_neurons']

plt.axhline(y=offset)
plot_section(offset,num['inh_neurons'],'inhibit',color_inh)

plt.show()
