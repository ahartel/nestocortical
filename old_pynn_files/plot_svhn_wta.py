import numpy as np
import pickle
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from svhn_wta import num,tstop

file_stem = './Results/svhn_wta_np1_nest_'

color_input = 'red'
color_exc = 'green'
color_inh = 'blue'

#skiprows = 100000
plot_rates = True

def plot_section(ax1,offset,num_neurons,file_leaf,color,plot_rates,skiprows):
    ax1.set_xlabel('time [ms]')
    ax1.set_ylabel('neuron number')
    # prepare empty spike arrays
    spikes = [None] * num_neurons
    for j in range(num_neurons):
        spikes[j] = []
    # load spikes from file
    this_spikes = np.loadtxt(file_stem+file_leaf+'.ras',usecols=(0,1),ndmin=2,skiprows=skiprows)
    # create coarser time bins
    bins = np.arange(num['steps'])*tstop
    large_bins = np.arange(5+1)*1000
    rates = np.zeros(num['steps'])
    #second_rates = np.zeros(5)
    bin_count = 0
    #large_bin_count = 0
    for spike in this_spikes:
        spikes[int(spike[1])].append(spike[0])
        try:
            while spike[0] > bins[bin_count+1]:
                bin_count += 1
        except IndexError:
            pass
        rates[bin_count] += 1

        #while spike[0] > large_bins[large_bin_count+1]:
        #    large_bin_count += 1
        #second_rates[large_bin_count] += 1

    rates /= num_neurons*tstop/1000
    #second_rates /= num_neurons

    for j in range(num_neurons):
        ax1.plot(spikes[j],np.ones(len(spikes[j]))*(offset+j),linestyle='',marker='|',color=color)

    ax2 = ax1.twinx()
    ax2.plot(bins,rates)
    ax2.set_ylabel('firing rate [Hz]')
    #ax2.plot(large_bins[0:5],second_rates)

def plot_input_numbers():
    for i in range(1,num['steps']):
        plt.axvline(x=i*50,color='grey')

    with open('%slabels.txt'%(file_stem,),'r') as f:
        cnt = 0
        for line in f.readlines(): 
            plt.text(cnt*50+25,10,line)
            cnt += 1

if 1:
    fig = plt.figure()
    offset = 0
    ax0 = plt.subplot(511)
    plot_section(ax0,offset,num['inputs'],'input',color_input, plot_rates, 0)

    ax1 = plt.subplot(512,sharex=ax0)
    plot_section(ax1,offset,num['l0_exc_neurons'],'exc_0',color_exc, plot_rates, 0)
    plot_input_numbers()

    ax2 = plt.subplot(513,sharex=ax0)
    plot_section(ax2,offset,num['l0_inh_neurons'],'inh_0',color_inh, plot_rates, 0)

    ax3 = plt.subplot(514,sharex=ax0)
    plot_section(ax3,offset,num['l1_inh_neurons'],'inh_1',color_inh, plot_rates, 0)

    ax4 = plt.subplot(515,sharex=ax0)
    plot_section(ax4,offset,num['l1_exc_neurons'],'exc_1',color_exc, plot_rates, 0)



# weights
if 1:
    fig = plt.figure()
    (input_wgt,l1_wgt) = pickle.load(open("%sinitial_weights.wgt"%(file_stem,)))
    plt.subplot(221)
    plt.imshow(input_wgt,interpolation='nearest',aspect='auto')
    plt.colorbar(orientation='vertical')
    plt.subplot(223)
    plt.imshow(l1_wgt,interpolation='nearest',aspect='auto')
    plt.colorbar(orientation='vertical')
    (input_wgt,l1_wgt) = pickle.load(open("%sfinal_weights.wgt"%(file_stem,)))
    plt.subplot(222)
    plt.imshow(input_wgt,interpolation='nearest',aspect='auto')
    plt.colorbar(orientation='vertical')
    plt.subplot(224)
    plt.imshow(l1_wgt,interpolation='nearest',aspect='auto')
    plt.colorbar(orientation='vertical')

plt.show()
