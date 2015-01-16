#!/bin/python
import os
import numpy as np
from sets import Set
import matplotlib.pyplot as plt

image_width = 16
image_height = 16

if not os.path.exists('results'):
    os.makedirs('results')
#os.system('../../bin/xnet_balls 256 '+os.getcwd()+'/results/')
# plot weight differences for neurons that have fired
# collect all neurons with index > 511 that have fired
#data = numpy.loadtxt('./results/xnet_balls_spikes.dat', delimiter=',')
#neurons = []
#for line in data:
#    if line[0] > 511:
#        neurons.append(int(line[0]))
#print Set(neurons)
# turns out that all neurons fired anyway

for neuron in range(512,560):
    initial = np.loadtxt('./results/xnet_balls_weights_initial_'+str(neuron))
    final   = np.loadtxt('./results/xnet_balls_weights_final_'+str(neuron))

    weight_diff = []
    for px in range(0,image_height*image_width):
        diff_on  = final[2*px] - initial[2*px]
        diff_off = final[2*px+1] - initial[2*px+1]
        result = 0
        if diff_on > 0 and diff_off > 0:
            result = 3
        elif diff_on > 0 and diff_off <= 0:
            result = 1
        elif diff_on < 0 and diff_off > 0:
            result = 2
        try:
            weight_diff[px/image_width].append(result)
        except IndexError:
            weight_diff.append([])
            weight_diff[px/image_width].append(result)

    plt.figure()
    plt.imshow(weight_diff)

plt.show()
