import numpy as np
from svhn_wta import num,tstop
import matplotlib.pyplot as plt

file_stem = './Results/svhn_wta_np1_nest_'

def plot_membranes(file_leaf,num_neurons,skiprows=0):
    neurons = [[] for i in range(num_neurons)]
    times = [[] for i in range(num_neurons)]
    membranes = np.loadtxt(file_stem+file_leaf+'.v',usecols=(0,1,2),ndmin=2,skiprows=skiprows,)
    
    for v in membranes:
        neurons[int(v[0])].append(v[2])
        times[int(v[0])].append(v[1])

    for n in range(num_neurons): 
        plt.plot(times[n],neurons[n])

plot_membranes('exc_0',num['l0_exc_neurons'])
plt.show()
