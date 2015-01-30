#!/bin/python
import os, sys
sys.path.append('../../python')
import numpy as np
from sets import Set
import matplotlib.pyplot as plt
import neuroplotlib as nplt

image_width = 16
image_height = 16
num_repetitions = 12000
neurons = range(512,560)

#print plt.style.available
#plt.style.context('fivethirtyeight')

if not os.path.exists('results'):
    os.makedirs('results')

#os.system('../../bin/xnet_balls_rect 0 '+str(num_repetitions)+' '+os.getcwd()+'/results/')
print "Simulation done."

if 0:
    plt.figure()
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

        plt.subplot(6,8,neuron-neurons[0]+1)
        plt.title(neuron)
        plt.imshow(weight_diff)
        plt.colorbar()

# load order
stimuli = np.loadtxt('./results/xnet_balls_order',delimiter=',')
# load spikes
data = np.loadtxt('./results/xnet_balls_spikes.dat', delimiter=',')

if 1:
    # generate Peri-Stimulus Time Histogram
    psth = nplt.psth.psth(stimuli, data, neurons, 10)

    #import pprint
    #pp = pprint.PrettyPrinter()
    #pp.pprint(psth[0.0])

    fig, axes = plt.subplots(nrows=len(psth), ncols=5)

    for ax, col in zip(axes[0], range(len(psth.itervalues().next()))):
        ax.set_title(col)

    for ax, row in zip(axes[:,0], psth):
        ax.set_ylabel(row)

    x = 0
    y = 0
    for stimulus,groups in psth.iteritems():
        # plot some groups
        for group in [groups[0],groups[1],groups[2],groups[3],groups[-2]]:
            ax = axes[y][x]
            ax.set_ylim(neurons[0],neurons[-1])
            ax.set_xlim(0,0.1)
            ax.grid()
            for nrn, times in group.iteritems():
                mean = np.mean(times)
                std = np.std(times)
                num = len(times)
                ax.errorbar(mean,nrn,xerr=std,marker='o',color=str(1.0-float(num)/15.0))
                ax.annotate(str(num),xy=(mean,nrn))

            x += 1
        y += 1
        x = 0

plt.figure()
stim_count = 0
for stimulus,groups in psth.iteritems():
    plt.subplot(len(psth),1,stim_count)
    # calculate specialization value
    metrics = []
    #if stim_count == 0:
    #    print stimulus," ",len(groups)
    for group in groups:
        #if stim_count == 0:
        #    print "==group=="
        metric = 0
        for nrn,times in group.iteritems():
            std = np.std(times)
            num = float(len(times))
            #if stim_count == 0:
            #    print " ",nrn," ",num," ",std
            metric += num/(std+0.001)

        metric /= len(group)
        metrics.append(metric)

    plt.plot(metrics)
    plt.grid()
    plt.ylabel(stimulus)

    stim_count += 1

plt.figure()
nplt.spikes.plot_spikes(data)

ranges = []
for st in stimuli[stimuli[:,0]==90.0]:
    ranges.append((float(st[1]),float(st[1]+0.2)))

#plt.figure()
#nplt.spikes.plot_spikes_ranges(data,ranges)


# show figures
plt.show()


