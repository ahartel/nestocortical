import sys, copy
from nest import *
import nest.topology as tp
import numpy as np
from pylab import cm
import matplotlib.pyplot as plt

# This package generates 28 by 28 pixel images
# It can also generate the input poisson spikes directly
# Has to be tested whether this is faster than the Pynn Poisson sources
import SEM_input



seed = 764756387
tshow = 40.0 # ms
tpaus = 10.0
input_rate = 40.0 # Hz
cell_params_lif = {
               'V_th'  :-55.0,  # mV
               'g_L'     : 10.0,  # ms 
               'tau_syn_ex' :  2.5,  # ms
               'tau_syn_in' :  5.0,  # ms
            }

# values taken from Naud et al. 2008
cell_params_adex = {
                'C_m'        :  200.0,  # pF
                'g_L'     : 10.0,  # ms
                #'tau_refrac':  2.0,  # ms
                'V_th'  :-50.0,  # mV
                #'tau_syn_E' :  2.5,  # ms
                #'tau_syn_I' :  5.0,  # ms
                'E_L'    :-58.0,  # mV
                'a'         :  2.0,  # nS
                'b'         :100.0,  # pA
                # V_T and delta_t default OK
                'tau_w'     :120.0,  # ms
                'V_reset'   :-46.0,  # mV
                'tau_syn_ex': 1.0,
                'tau_syn_in': 1.5,
                'gsl_error_tol': 1e-8,
    }

SetDefaults('iaf_cond_exp',cell_params_lif)
#SetDefaults('aeif_cond_exp',{'tau_syn_ex':1.5})
#SetDefaults('aeif_cond_exp',{'tau_syn_in':1.5})
SetDefaults('aeif_cond_exp',cell_params_adex)
import pprint
pp = pprint.PrettyPrinter()
pp.pprint(GetDefaults('iaf_cond_exp'))
pp.pprint(GetDefaults('aeif_cond_exp'))
#pp.pprint(GetDefaults('aeif_cond_exp'))
#sys.exit(0)

SetStatus([0],{'overwrite_files':True})

num = {}
num['l0_exc_neurons'] = 20
num['l0_exc_maxneighbors'] = 4
num['l1_exc_neurons'] = 4
num['l1_exc_maxneighbors'] = 4
num['l0_l1_maxneighbors'] = 4
num['l0_inh_neurons'] = 20
num['l1_inh_neurons'] = 5
num['inputs'] = SEM_input.SEM_input_config['num_inputs']
print num['inputs']
num['inputs_maxneighbors'] = 4
num['steps'] = 20
num['steps_firing_rate_average'] = 10


# input -> exc0
w_inp_exc0_peak = 0.2
sigma_inp_exc0 = num['inputs']/3.0
w_inp_exc0_max = 1.

# exc0 -> exc1
sigma_exc0_exc1 = 4.
w_exc0_exc1_peak = 0.005
w_exc0_exc1_max = 0.005

# exc0 -> inh0
p_exc0_inh0 = 1.0
w_exc0_inh0 = 10.0

# exc0 -> exc0
sigma_exc0_exc0 = 0.5
w_exc0_exc0_max = 0.5

# exc1 -> exc1
sigma_exc1_exc1 = 7.
w_exc1_exc1_max = 0.001

# exc1 -> inh1
p_exc1_inh1 = 1.0
w_exc1_inh1 = 0.02

# inh0 -> exc0
p_inh0_exc0 = 1.0
w_inh0_exc0 = -150.0

# inh1 -> exc1
p_inh1_exc1 = 1.0
w_inh1_exc1 = 0.1


def plot_neurons(meters,k,m,variables,title):
    plt.figure()
    plt.suptitle(title)
    start = len(variables)*100+11
    for var in variables:
        plt.subplot(start)
        plt.grid()
        for i in range(k,m):
            #meter = tp.GetElement(meters,[i,0])
            events = GetStatus([meters[i]])[0]['events'] 
            t = events['times']
            plt.plot(t, events[var])
            plt.ylabel(var)
        start = start + 1

def plot_weights(layer,target):
    status = GetStatus(layer)[0]
    image_width = SEM_input.SEM_input_config['image_width']
    weights = np.zeros((image_width,image_width))
    for i in range(0,image_width):
        for j in range(0,image_width):
            pixel = (i*image_width+j)*2
            status = GetStatus(FindConnections(tp.GetElement(layer,[pixel,0])))
            for s in status:
                if s['target'] == target:
                    weights[i][j] = s['weight']

    plt.figure()
    #plt.hist(weights,bins=100)
    #cmap = plt.get_cmap('grey')
    plt.title(str(target))
    plt.imshow(weights)
    plt.colorbar()

def plot_layer(layer):
    tp.PlotLayer(layer, nodesize=50)
    status = GetStatus(layer)[0]
    extent = status['topology']['extent']
    # beautify
    plt.axis([extent[0]/(-2.0)-0.25, extent[0]/2.0+0.25, extent[1]/(-2.0)-0.25, extent[1]/2.0+0.25])
    plt.axes().set_aspect('equal', 'box')
    plt.axes().set_xticks([w-extent[0]/2.0 for w in range(int(extent[0])+1)])
    plt.axes().set_yticks([w-extent[1]/2.0 for w in range(int(extent[1])+1)])
    plt.grid(True)
    plt.xlabel('%d Columns, Extent: %f' % (status['topology']['columns'],extent[0]))
    plt.ylabel('%d Rows, Extent: %f' % (status['topology']['rows'],extent[1]))

def setup_network():

    print "[ Creating excitatory population ]"
    # 1) create excitatory populations
    l0_exc_population =  tp.CreateLayer ({
                                'rows' : 1 ,
                                'columns' : num['l0_exc_neurons'],
                                'extent' : [ float(num['l0_exc_neurons']), 1.  ],
                                'elements' : 'aeif_cond_exp',
                                'edge_wrap' : True } )


    print "[ Creating inhibitory population ]"
    # 2) create inhibitory population
    l0_inh_population =  tp.CreateLayer ({
                                'rows' : 1,
                                'columns' : num['l0_inh_neurons'],
                                'extent' : [ float(num['l0_inh_neurons']), 1.  ] ,
                                'elements' : 'aeif_cond_exp',
                                'edge_wrap' : True } )


    print "[ Projecting excitatory -> inhibitory population ]"
    # 3) exc -> inh
    CopyModel('static_synapse','exc_inh', {'weight':w_exc0_inh0})
    l0_exc_inh_dict = {
                'connection_type' : 'convergent',
                'mask': {
                    'rectangular': {
                        'lower_left': [-0.5,-0.5],
                        'upper_right':[0.5,0.5]
                    }
                },
                #'kernel':p_exc0_inh0,
                'synapse_model': 'exc_inh'
            }
    tp.ConnectLayers(l0_exc_population,l0_inh_population,l0_exc_inh_dict)


    print "[ Projecting excitatory -> excitatory population ]"
    # 4) exc -> exc
    # Since these connections are distance-dependent, we can use topological connections here
    CopyModel('static_synapse','exc_exc',{'weight':w_exc0_exc0_max})
    l0_exc_exc_dict = {
                'connection_type': 'convergent',
                'mask': {
                    'rectangular': {
                        'lower_left': [float(num['l0_exc_neurons']/(-2.0)),-0.5],
                        'upper_right':[float(num['l0_exc_neurons']/(2.0)),0.5]
                    }
                },
                'synapse_model': 'exc_exc',
                'weights': {
                    'gaussian': {'p_center': 1., 'sigma': sigma_exc0_exc0}
                }
            }
    tp.ConnectLayers(l0_exc_population,l0_exc_population,l0_exc_exc_dict)


    print "[ Projecting inhibitory -> excitatory population ]"
    # 5) inh -> exc
    CopyModel('static_synapse','inh_exc', {'weight':w_inh0_exc0})
    l0_inh_exc_dict = {
                'connection_type' : 'convergent',
                'mask': {
                    'grid': {
                        'rows': 1,
                        'columns': num['l0_inh_neurons']-1,
                    },
                    'anchor': {
                        'row': 0,
                        'column': -1,
                    }
                },
                #'kernel':p_inh0_exc0,
                'synapse_model': 'inh_exc'
            }
    tp.ConnectLayers(l0_inh_population,l0_exc_population,l0_inh_exc_dict)


    print "[ Creating input population ]"
    # 6) create input population
    CopyModel('poisson_generator','input_model',{'rate':40.0})
    input_population =  tp.CreateLayer ({
                                'rows' : 1 ,
                                'columns' : num['inputs'],
                                'extent' : [ float(num['inputs']), 1.  ],
                                'elements' : 'input_model',
                                'edge_wrap' : True } )

    parrot_population =  tp.CreateLayer ({
                                'rows' : 1 ,
                                'columns' : num['inputs'],
                                'extent' : [ float(num['inputs']), 1.  ],
                                'elements' : 'parrot_neuron',
                                'edge_wrap' : True } )


    print "[ Projecting input -> excitatory population ]"
    # 7) input -> exc
    CopyModel('static_synapse','input_parrot', {'weight': 1.0})
    CopyModel('stdp_synapse','parrot_exc', {'weight':w_inp_exc0_peak,'alpha':0.5,'Wmax':w_inp_exc0_max})
    CopyModel('static_synapse','parrot_inh', {'weight': w_inp_exc0_peak})
    input_parrot_dict = {
                'connection_type' : 'convergent',
                'mask': {
                    'rectangular': {
                        # this is intended: only connect to one neuron!
                        'lower_left': [-0.5,-0.5],
                        'upper_right':[0.5,0.5]
                    }
                },
                'synapse_model': 'input_parrot'
            }
    parrot_exc_dict = {
                'connection_type' : 'convergent',
                'mask': {
                    'grid': {
                        'rows': 1,
                        'columns': num['inputs'],
                    },
                    'anchor': {
                        'row': 0,
                        'column': 0,
                    }
                },
                'kernel': {'gaussian': {'p_center':1.0,'sigma':sigma_inp_exc0}},
                'synapse_model': 'parrot_exc'
            }

    parrot_inh_dict = copy.copy(parrot_exc_dict)
    parrot_inh_dict['synapse_model'] = 'parrot_inh'

    tp.ConnectLayers(input_population,parrot_population,input_parrot_dict)
    tp.ConnectLayers(parrot_population,l0_exc_population,parrot_exc_dict)
    #tp.ConnectLayers(parrot_population,l0_inh_population,parrot_inh_dict)


    return l0_exc_population,l0_inh_population,input_population,parrot_population

# CREATE
populations = setup_network()
#plot_layer(populations[2])
#plot_layer(populations[3])
#plt.figure() #ugly stack cleaning
#print GetStatus(populations[0])
#print GetStatus(populations[2])
#for i in range(num['l0_exc_neurons']):
#    print GetStatus(tp.GetElement(populations[0],[i,0]))
#for i in range(num['l0_inh_neurons']):
#    print GetStatus(tp.GetElement(populations[1],[i,0]))
#    tgts = GetStatus(FindConnections(tp.GetElement(populations[1],[i,0])))
#    print tgts
#connPlot(populations[2],'input_model','aeif_cond_exp','input_exc','title')
plot_weights(populations[3],2)
plot_weights(populations[3],3)
plot_weights(populations[3],4)
plot_weights(populations[3],5)

# CONNECT READOUTS
#connect_readouts(l0_exc_population,l0_inh_population,input_population)
voltmeters = Create('multimeter',num['l0_exc_neurons']+num['l0_inh_neurons'],{'to_file':True,'record_from':['V_m','g_ex','g_in']})
spikedetectors = Create('spike_detector',4,{'precise_times':True,'to_file':True})
for n,pop in enumerate(populations):
    SetStatus([spikedetectors[n]],{'label':str(n)})
    tgts = [nd for nd in GetLeaves(populations[n])[0]] 
    ConvergentConnect(tgts,[spikedetectors[n]])


tgts = [nd for nd in GetLeaves(populations[0])[0]] 
for i in range(num['l0_exc_neurons']):
    DivergentConnect([voltmeters[i]],[tgts[i]])
tgts = [nd for nd in GetLeaves(populations[1])[0]] 
for i in range(num['l0_inh_neurons']):
    DivergentConnect([voltmeters[i+4]],[tgts[i]])


# GENERATE INPUT
inputs = [nd for nd in GetLeaves(populations[2])[0]] 
for i in range(num['steps']):

    image = SEM_input.draw_image(SEM_input.SEM_input_config['centers'][i%4],SEM_input.SEM_input_config)

    # prepare input population firing rates
    for j in range(SEM_input.SEM_input_config['image_width']):
        for k in range(SEM_input.SEM_input_config['image_width']):
            SetStatus([inputs[2*j*SEM_input.SEM_input_config['image_width']+k*2]],{'rate': SEM_input.SEM_input_config['input_on_rate'] if (image[j][k] > 0.0) else SEM_input.SEM_input_config['input_off_rate']})
            SetStatus([inputs[2*j*SEM_input.SEM_input_config['image_width']+k*2+1]],{'rate': SEM_input.SEM_input_config['input_on_rate'] if (image[j][k]<1.0) else SEM_input.SEM_input_config['input_off_rate']})

    print "[Running simulation step %d]" % (i)
    Simulate(tshow)

    for j in range(SEM_input.SEM_input_config['image_width']):
        for k in range(SEM_input.SEM_input_config['image_width']):
            SetStatus([inputs[2*j*SEM_input.SEM_input_config['image_width']+k*2]],{'rate': 0.0})
            SetStatus([inputs[2*j*SEM_input.SEM_input_config['image_width']+k*2+1]],{'rate': 0.0})

    Simulate(tpaus)

    #for neuron in range(num['l0_exc_neurons']):
    #    events_ex = GetStatus([spikedetectors[neuron]],'n_events')[0]
    #    rate = (events_ex-last_events[neuron])/(tshow+tpaus)/1e-3
    #    last_events[neuron] = events_ex
    #    #print rate
    #    SetStatus([GetLeaves(populations[0])[0][neuron]],{'g_L':(1+(rate-20.0)/20.0)*10.0})
    #    #if rate < 20.0:
    #    #    SetStatus([GetLeaves(populations[0])[0][neuron]],{'g_L':5.0})
    #    #elif rate > 30.0:
    #    #    SetStatus([GetLeaves(populations[0])[0][neuron]],{'g_L':15.0})
    #    #else:                                              
    #    #    SetStatus([GetLeaves(populations[0])[0][neuron]],{'g_L':10.0})

plot_weights(populations[3],2)
plot_weights(populations[3],3)
plot_weights(populations[3],4)
plot_weights(populations[3],5)
plt.show()
# PRINT
PrintNetwork(depth=2)
