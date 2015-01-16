#!/bin/python
import os
import numpy as np
from sets import Set
import matplotlib.pyplot as plt

image_width = 16
image_height = 16
num_repetitions = 120

if not os.path.exists('results'):
    os.makedirs('results')

#os.system('../../bin/xnet_balls '+str(num_repetitions)+' '+os.getcwd()+'/results/')

neurons = range(512,560)
# load order
order = np.loadtxt('./results/xnet_balls_order',delimiter=',')
order_count = 0
psth_groups = {}
angle_times = {}
angles = [0,45,90,135,180,225,270,315]
for angle in angles:
    psth_groups[angle] = []
    angle_times[angle] = []

# plot weight differences for neurons that have fired
# collect all neurons with index > 511 that have fired
if 1:
    data = np.loadtxt('./results/xnet_balls_spikes.dat', delimiter=',')
    plt.plot(data[:,1], data[:,0],'o')
    angle = order[order_count][2]
    angle_times[angle].append(order[order_count][1])
    for line in data:
        neuron = line[0]
        if neuron > 511:
            while order_count < len(order)-1 and line[1] > order[order_count+1][1]:
                order_count += 1
                angle = order[order_count][2]
                angle_times[angle].append(order[order_count][1])
            psth_groups[angle].append((line[0],line[1]))

    print psth_groups
    print angle_times

    group_by = 10
    for angle in angles:
        print "Angle ", angle
        group_count = 0
        for spike in psth_groups[angle]:
            print spike
            while spike[1] > angle_times[angle][group_count+1]:
                group_count += 1
            print "Presentation: ",group_count
            new_time = spike[1]-angle_times[angle][group_count]
            print new_time

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

plt.show()
