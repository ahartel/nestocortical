import sys
import numpy as np
import matplotlib.pyplot as plt

def plot_spikes(data,show=False):
    plt.plot(data[:,1],data[:,0],'o')
    plt.grid()

    if show:
        plt.show()

def plot_spikes_ranges(data,ranges,show=False):
    range_pointer = 0
    data_pointer = 0
    current_range = ranges[range_pointer]
    while data_pointer < len(data):
        # let's assume that the current line fits into the current range
        line = data[data_pointer]
        data_range_begin = data_pointer
        data_range_end = -1
        while line[1] >= current_range[0] and line[1] < current_range[1]:
            data_range_end = data_pointer
            data_pointer += 1
            if data_pointer==len(data):
                break
            line = data[data_pointer]

        if data_range_end >= 0:
            plt.plot(data[data_range_begin:data_range_end,1],data[data_range_begin:data_range_end,0],'bo')

        if data_pointer == len(data):
            break

        # if this is not the case, and line[1] is still too early,
        # drop some lines
        while line[1] < current_range[0]:
            data_pointer += 1
            if data_pointer == len(data):
                break
            line = data[data_pointer]

        # if the line is too large for the current range, we'll have to
        # increase the current range
        while line[1] >= current_range[1]:
            range_pointer += 1
            if range_pointer == len(ranges):
                break
            current_range = ranges[range_pointer]

        if range_pointer == len(ranges):
            break


    plt.grid()

    if show:
        plt.show()

def plot_spikes_file(filename,show=False):
    data = np.loadtxt(filename,delimiter=',',ndmin=2)
    plot_spikes(data,show)

def plot_spikes_rate(filename,show=False):
    binning = 0.05

    data = np.loadtxt(filename,delimiter=',',ndmin=2)

    ax1 = plt.subplot(211)
    plt.plot(data[:,1],data[:,0],'o')
    plt.grid()
    plt.subplot(212, sharex=ax1)
    bins = np.arange(int(data[0][1]*1000.0),int(data[-1][1]*1000.0),int(binning*1000.0))
    hist,bin_edges = np.histogram(data[:,1]*1000,bins=bins)
    plt.plot(bins[1:]/1000.0,hist/binning)
    plt.grid()

    if show:
        plt.show()

if __name__ == '__main__':
    plot_spikes(sys.argv[1],True)

