#!/bin/python
import os, sys
import numpy as np
from sets import Set
import matplotlib.pyplot as plt

image_width = 16
image_height = 16
num_repetitions = 1000
neurons = range(512,560)

color_lookup = [ '#111111','#222222','#333333','#444444','#555555',
    '#666666','#777777','#888888','#999999','#aaaaaa',
    '#bbbbbb','#cccccc','#dddddd','#eeeeee','#ffffff']

#print plt.style.available
#plt.style.context('fivethirtyeight')

if not os.path.exists('results'):
    os.makedirs('results')

os.system('../../bin/xnet_pong '+str(num_repetitions)+' '+os.getcwd()+'/results/')

if 0:
    for neuron in neurons:
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
        plt.title(neuron)
        plt.imshow(weight_diff)

# load record
game_record = np.loadtxt('./results/pong_record',delimiter=',',skiprows=1)
# load spikes
#data = np.loadtxt('./results/xnet_pong_spikes.dat', delimiter=',')

plt.plot(game_record[:,0],game_record[:,2])
plt.plot(game_record[:,0],game_record[:,3])

# show figures
plt.show()


