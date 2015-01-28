#!/bin/python
import os, sys
import numpy as np
from sets import Set
import matplotlib.pyplot as plt

image_width = 16
image_height = 16
num_repetitions = 10000
intermediate_neurons = range(272,304)
output_neurons = range(304,320)

color_lookup = [ '#111111','#222222','#333333','#444444','#555555',
    '#666666','#777777','#888888','#999999','#aaaaaa',
    '#bbbbbb','#cccccc','#dddddd','#eeeeee','#ffffff']

#print plt.style.available
#plt.style.context('fivethirtyeight')

if not os.path.exists('results'):
    os.makedirs('results')

os.system('../../bin/xnet_pong_poisson_rect '+str(num_repetitions)+' '+os.getcwd()+'/results/')
print "Simulation done."

if 1:
    plt.figure()
    for neuron in intermediate_neurons:
        # load weights
        initial = np.loadtxt('./results/xnet_pong_weights_initial_'+str(neuron))
        final   = np.loadtxt('./results/xnet_pong_weights_final_'+str(neuron))

        weight_diff = []
        for y in range(0,image_height):
            for x in range(0,image_width):
                diff = final[x*image_width+y]-initial[x*image_width+y]
                try:
                    weight_diff[y].append(diff)
                except IndexError:
                    weight_diff.append([])
                    weight_diff[y].append(diff)

        plt.subplot(4,8,neuron-intermediate_neurons[0]+1)
        plt.title(neuron)
        imgplot = plt.imshow(weight_diff, interpolation='none',origin='lower')
        imgplot.set_cmap('binary')
        plt.colorbar()

    plt.figure()
    for neuron in output_neurons:
        # load weights
        initial = np.loadtxt('./results/xnet_pong_weights_initial_'+str(neuron))
        final   = np.loadtxt('./results/xnet_pong_weights_final_'+str(neuron))

        weight_diff = []
        for x in range(0,4):
            for y in range(0,8):
                diff = final[x*8+y]-initial[x*8+y]
                try:
                    weight_diff[x].append(diff)
                except IndexError:
                    weight_diff.append([])
                    weight_diff[x].append(diff)

        plt.subplot(4,4,neuron-output_neurons[0]+1)
        plt.title(neuron)
        imgplot = plt.imshow(weight_diff, interpolation='none',origin='lower')
        imgplot.set_cmap('binary')
        plt.colorbar()

plt.figure()
# load record
game_record = np.loadtxt('./results/pong_record',delimiter=',',skiprows=1)
ax1 = plt.subplot(211)
plt.plot(game_record[:,0],game_record[:,2])
plt.plot(game_record[:,0],game_record[:,3])

plt.subplot(212, sharex=ax1)
hits = 0
counter = 0
last_time = 0
for t,x,y,p in game_record:
    if x>7.99:
        #plt.axvline(t,color='red')
        if abs(y-p)<=0.5:
            hits += 1
        counter += 1
        if counter==10:
            plt.plot(t,float(hits)/(t-last_time),'o',color='blue')
            last_time = t
            counter = 0
            hits = 0

plt.figure()
spikes = np.loadtxt('./results/xnet_pong_spikes.dat',delimiter=',')
plt.plot(spikes[:,1],spikes[:,0],'o')
plt.grid()

# show figures
plt.show()


