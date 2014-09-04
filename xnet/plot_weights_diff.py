import sys
import numpy as np
import matplotlib.pyplot as plt

initial = np.loadtxt(sys.argv[1],delimiter=' ')
final = np.loadtxt(sys.argv[2],delimiter=' ')
height = int(sys.argv[3])

neuron_initial = []
neuron_final   = []
for ii,w in enumerate(zip(initial,final)):
    neuron_initial.append(w[0])
    neuron_final.append(w[1])
    if (ii+1)%height == 0:
        neuron_diff = np.array(neuron_final) - np.array(neuron_initial)
        if (ii+1 == height*10):
            plt.imshow(neuron_diff)
            plt.colorbar()
        neuron_initial = []
        neuron_final  = []

plt.show()
