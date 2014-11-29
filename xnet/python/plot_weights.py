import sys
import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt(sys.argv[1],delimiter=' ')
height = int(sys.argv[2])

neuron_data = []
for ii,line in enumerate(data):
    neuron_data.append(line)
    if (ii+1)%height == 0:
        if (ii+1 == height*10):
            plt.imshow(neuron_data)
        neuron_data = []

plt.show()
