import numpy as np
import matplotlib.pyplot as plt
from svhn_wta import num

file_stem = './Results/svhn_wta_np1_nest_'

color_input = 'red'
color_exc = 'green'
color_inh = 'blue'

def plot_section(offset,num,file_leaf,color):
    spikes = [None] * num
    for j in range(num):
        spikes[j] = []
    this_spikes = np.loadtxt(file_stem+file_leaf+'.ras',usecols=(0,1),ndmin=2)
    for spike in this_spikes:
        spikes[int(spike[1])].append(spike[0])
    for j in range(num):
        plt.plot(spikes[j],np.ones(len(spikes[j]))*(offset+j),linestyle='',marker='|',color=color)

offset = 0
#plot_section(offset,num['inputs'],'input',color_input)

offset = num['inputs']
plt.axhline(y=offset)
plot_section(offset,num['l0_exc_neurons'],'exc_0',color_exc)

offset += num['l0_exc_neurons']
plt.axhline(y=offset)
plot_section(offset,num['l1_exc_neurons'],'exc_1',color_exc)

offset += num['l1_exc_neurons']
plt.axhline(y=offset)
plot_section(offset,num['l0_inh_neurons'],'inh_0',color_inh)

offset += num['l0_inh_neurons']
plt.axhline(y=offset)
plot_section(offset,num['l1_inh_neurons'],'inh_1',color_inh)

for i in range(1,num['steps']):
    plt.axvline(x=i*50,color='grey')

with open('%slabels.txt'%(file_stem,),'r') as f:
    cnt = 0
    for line in f.readlines(): 
        plt.text(cnt*50+25,1000,line)
        cnt += 1

plt.show()
