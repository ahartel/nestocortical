#!/bin/python
import os, sys
import numpy as np
from sets import Set
import matplotlib.pyplot as plt
from psth import psth

image_width = 16
image_height = 16
num_repetitions = 2000
neurons = range(512,560)

#print plt.style.available
#plt.style.context('fivethirtyeight')

if not os.path.exists('results'):
    os.makedirs('results')

os.system('../../bin/xnet_balls '+str(num_repetitions)+' '+os.getcwd()+'/results/')

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

# load order
stimuli = np.loadtxt('./results/xnet_balls_order',delimiter=',')
# load spikes
data = np.loadtxt('./results/xnet_balls_spikes.dat', delimiter=',')
# generate Peri-Stimulus Time Histogram
psth = psth(stimuli, data, 10)

#import pprint
#pp = pprint.PrettyPrinter()
#pp.pprint(psth[0.0])

fig, axes = plt.subplots(nrows=len(psth), ncols=3)

for ax, col in zip(axes[0], range(len(psth.itervalues().next()))):
    ax.set_title(col)

for ax, row in zip(axes[:,0], psth):
    ax.set_ylabel(row)

x = 0
y = 0
for stimulus,groups in psth.iteritems():
    for group in [groups[0],groups[5],groups[-1]]:
        ax = axes[y][x]
        for nrn, times in group.iteritems():
            mean = np.mean(times)
            std = np.std(times)
            num = len(times)
            ax.errorbar(mean,nrn,xerr=std,marker='o',color=str(float(num)/20.0))
            ax.annotate(str(num),xy=(mean,nrn))

        x += 1
    y += 1
    x = 0

plt.figure()
plt.plot(data[:,1],data[:,0],'o')
plt.grid()

# show figures
plt.show()


