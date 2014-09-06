import sys, argparse
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('--start', help='linspace start value', type=float, dest='start')
parser.add_argument('--stop', help='linspace stop value', type=float, dest='stop')
parser.add_argument('--num', help='linspace num value', type=int, dest='num')

args=parser.parse_args()

# load spike data
data = np.loadtxt(sys.argv[1],delimiter=',')
# create time bins every 100 ms
# every second time bin codes for a ball passing by in a certain direction
bins = np.linspace(args.start,args.stop,args.num)
# this dict contains a list of neurons for every time bin
times = {}

# sort spikes by neurons
spikes = [[] for n in range(48)]
for sp in data:
    spikes[int(sp[0])].append(sp[1])

# digitize spike times of every neuron and and the neuron's id to the times dict
for n,neuron_spikes in enumerate(spikes):
    try:
        digitized = np.digitize(neuron_spikes, bins)
        for bin in digitized:
            try:
                times[bin].append(n)
            except KeyError:
                times[bin] = [n]
    except ValueError:
        print "No spikes for neuron ",n

for bin,neurons in times.items():
    print "Spikes in bin ",bin,":"
    print neurons


