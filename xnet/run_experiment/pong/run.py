#!/bin/python
import os, sys
import numpy as np
from sets import Set
import matplotlib.pyplot as plt

image_width = 16
image_height = 16
num_repetitions = 5000
neurons = range(48,64)

color_lookup = [ '#111111','#222222','#333333','#444444','#555555',
    '#666666','#777777','#888888','#999999','#aaaaaa',
    '#bbbbbb','#cccccc','#dddddd','#eeeeee','#ffffff']

#print plt.style.available
#plt.style.context('fivethirtyeight')

if not os.path.exists('results'):
    os.makedirs('results')

os.system('../../bin/xnet_pong_class '+str(num_repetitions)+' '+os.getcwd()+'/results/')
print "Simulation done."

if 1:
    plt.figure()
    for neuron in neurons:
        # load weights
        initial = np.loadtxt('./results/xnet_pong_weights_initial_'+str(neuron))
        final   = np.loadtxt('./results/xnet_pong_weights_final_'+str(neuron))

        weight_diff = []
        for x in range(0,image_width):
            diff = final[x]#-initial[x]
            try:
                weight_diff[x].append(diff)
            except IndexError:
                weight_diff.append([])
                weight_diff[x].append(diff)

        for y in range(0,image_height):
            diff = final[image_width+y]#-initial[image_width+y]
            weight_diff[y].append(diff)

        plt.subplot(4,4,neuron-47)
        plt.title(neuron)
        plt.imshow(weight_diff, interpolation='none')
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
            plt.plot(t,float(hits)/(t-last_time),'o')
            last_time = t
            counter = 0
            hits = 0

plt.figure()
spikes = np.loadtxt('./results/xnet_pong_spikes.dat',delimiter=',')
plt.plot(spikes[:,1],spikes[:,0],'o')
plt.grid()

# show figures
plt.show()


