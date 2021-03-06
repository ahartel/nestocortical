import sys, copy
from nest import *
import nest.topology as tp
import numpy as np
from pylab import cm
import matplotlib.pyplot as plt
import pickle

# This package generates 28 by 28 pixel images
# It can also generate the input poisson spikes directly
# Has to be tested whether this is faster than the Pynn Poisson sources
import SEM_input

last_events = [0,0,0,0]
results_dir = './results'
with_plot_weights = False
with_homeostatis = False

seed = 764756387
tshow = 40.0 # ms
tpaus = 10.0
input_rate = 40.0 # Hz
cell_params_lif_cond = {
               'V_th'  :-55.0,  # mV
               'g_L'     : 10.0,  # ms 
               'tau_syn_ex' :  2.0,  # ms
               'tau_syn_in' :  3.0,  # ms
               'tau_minus' : 20.0,
               't_ref':5.0,
            }

cell_params_lif = {
               'tau_m'     : 5.0,  # ms 
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

#SetDefaults('iaf_cond_exp',cell_params_lif_cond)
SetDefaults('iaf_neuron',cell_params_lif)
#SetDefaults('aeif_cond_exp',cell_params_adex)
import pprint
pp = pprint.PrettyPrinter()
pp.pprint(GetDefaults('iaf_neuron'))
pp.pprint(GetDefaults('aeif_cond_exp'))
#pp.pprint(GetDefaults('aeif_cond_exp'))
#print GetStatus([0])
SetStatus([0],{'overwrite_files':True, 'data_path':results_dir})
#sys.exit(0)

num = {}
num['l0_exc_neurons'] = 4
num['l0_exc_maxneighbors'] = 4
num['l1_exc_neurons'] = 4
num['l1_exc_maxneighbors'] = 4
num['l0_l1_maxneighbors'] = 4
num['l0_inh_neurons'] = 4
num['l1_inh_neurons'] = 5
num['inputs'] = SEM_input.SEM_input_config['num_inputs']
num['inputs_inh_sources'] = 4
num['steps'] = 5000
num['steps_rate_average'] = 20


# input -> exc0
w_inp_exc0_peak = 180.0
sigma_inp_exc0 = num['inputs']/3.0
w_inp_exc0_max = 250.0
alpham_inp_exc0 = 0.01/200
alphap_inp_exc0 = alpham_inp_exc0*2
w_inp_exc0_min = 1.0

# input -> inh0
w_inp_inh0 = 150.0
sigma_inp_inh0 = num['inputs']/2.0

# exc0 -> exc1
sigma_exc0_exc1 = 4.
w_exc0_exc1_peak = 0.005
w_exc0_exc1_max = 0.005

# exc0 -> inh0
p_exc0_inh0 = 10.0
w_exc0_inh0 = 1000.0

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
w_inh0_exc0 = -1000.0

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

def dump_weights(layer,tag=''):
    layer_status = GetStatus(layer)[0]
    image_width = SEM_input.SEM_input_config['image_width']
    weights = []
    for i in range(0,image_width):
        for j in range(0,image_width):
            pixel = i*image_width+j
            status = GetStatus(FindConnections(tp.GetElement(layer,[pixel,0])))
            for s in status:
                weights.append((i,j,s['target'],s['weight']))

    pickle.dump(weights,open(results_dir+'/weights_'+str(layer_status['global_id'])+'_'+tag+'.dat','w'))

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
                                'elements' : 'iaf_neuron',
                                'edge_wrap' : True } )


    print "[ Creating inhibitory population ]"
    # 2) create inhibitory population
    l0_inh_population =  tp.CreateLayer ({
                                'rows' : 1,
                                'columns' : num['l0_inh_neurons'],
                                'extent' : [ float(num['l0_inh_neurons']), 1.  ] ,
                                'elements' : 'iaf_neuron',
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
    #tp.ConnectLayers(l0_exc_population,l0_exc_population,l0_exc_exc_dict)


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
    CopyModel('poisson_generator','input_model',{'rate':0.0})
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
    CopyModel('rect_stdp_synapse','parrot_exc', {'tau_plus': 10.0,'alpha_minus':alpham_inp_exc0,'alpha_plus':alphap_inp_exc0,'Wmax':w_inp_exc0_max})
    #CopyModel('static_synapse','parrot_exc')
    CopyModel('static_synapse','parrot_inh', {'weight': w_inp_inh0})
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
                #'kernel': {'gaussian': {'p_center':1.0,'sigma':sigma_inp_exc0}},
                'weights': {'uniform':{'min':w_inp_exc0_min,'max':w_inp_exc0_peak}},
                'synapse_model': 'parrot_exc'
            }

    parrot_inh_dict = copy.copy(parrot_exc_dict)
    #parrot_inh_dict['synapse_model'] = 'parrot_inh'
    #parrot_inh_dict['kernel'] = {'gaussian': {'p_center':1.0,'sigma':sigma_inp_exc0}}

    tp.ConnectLayers(input_population,parrot_population,input_parrot_dict)
    tp.ConnectLayers(parrot_population,l0_exc_population,parrot_exc_dict)
    #tp.ConnectLayers(parrot_population,l0_inh_population,parrot_inh_dict)

    # 7) input -> inh
    CopyModel('poisson_generator','inh_bias_model',{'rate':500.0})
    inh_bias_population =  tp.CreateLayer ({
                                'rows' : 1 ,
                                'columns' : num['inputs_inh_sources'],
                                'extent' : [ float(num['inputs_inh_sources']), 1.  ],
                                'elements' : 'inh_bias_model',
                                'edge_wrap' : True } )

    CopyModel('static_synapse','bias_inh', {'weight': w_inp_inh0})
    inh_bias_dict = {
                'connection_type' : 'convergent',
                'mask': {
                    'rectangular': {
                        # this is intended: only connect to one neuron!
                        'lower_left': [-0.5,-0.5],
                        'upper_right':[0.5,0.5]
                    }
                },
                'synapse_model': 'bias_inh',
                'weights': w_inp_inh0,
            }
    tp.ConnectLayers(inh_bias_population,l0_inh_population,inh_bias_dict)

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
if with_plot_weights:
    plot_weights(populations[3],2)
    plot_weights(populations[3],3)
    plot_weights(populations[3],4)
    plot_weights(populations[3],5)


# CONNECT READOUTS
# voltmeters
exc_voltmeters = Create('multimeter',num['l0_exc_neurons'],{'to_file':True,'record_from':['V_m'],'to_memory':False})
inh_voltmeters = Create('multimeter',num['l0_inh_neurons'],{'to_file':True,'record_from':['V_m'],'to_memory':False})

tgts = [nd for nd in GetLeaves(populations[0])[0]] 
for i in range(num['l0_exc_neurons']):
    SetStatus([exc_voltmeters[i]],{'label':'mm_exc_'+str(i)})
    DivergentConnect([exc_voltmeters[i]],[tgts[i]])
tgts = [nd for nd in GetLeaves(populations[1])[0]] 
for i in range(num['l0_inh_neurons']):
    SetStatus([inh_voltmeters[i]],{'label':'mm_inh_'+str(i)})
    DivergentConnect([inh_voltmeters[i]],[tgts[i]])

# spike detectors
exc_spikedetectors = Create('spike_detector',num['l0_exc_neurons'],{'precise_times':True,'to_file':True,'to_memory':True})
exc_tgts = [nd for nd in GetLeaves(populations[0])[0]] 
#for t in exc_tgts:
#    print GetStatus([t])

for n in range(num['l0_exc_neurons']):
    SetStatus([exc_spikedetectors[n]],{'label':"sd_exc_"+str(n)})
    ConvergentConnect([exc_tgts[n]],[exc_spikedetectors[n]])

inh_spikedetectors = Create('spike_detector',num['l0_inh_neurons'],{'precise_times':True,'to_file':True,'to_memory':False})
inh_tgts = [nd for nd in GetLeaves(populations[1])[0]] 
for n in range(num['l0_inh_neurons']):
    SetStatus([inh_spikedetectors[n]],{'label':"sd_inh_"+str(n)})
    ConvergentConnect([inh_tgts[n]],[inh_spikedetectors[n]])


inp_spikedetectors = Create('spike_detector',1,{'precise_times':True,'to_file':True})
inp_tgts = [nd for nd in GetLeaves(populations[3])[0]]
SetStatus([inp_spikedetectors[0]],{'label':"sd_inp_"+str(0)})

for n in range(num['inputs']):
    ConvergentConnect([inp_tgts[n]],[inp_spikedetectors[0]])

# DUMP INITIAL WEIGHTS
dump_weights(populations[3],'pre')

# GENERATE INPUT AND SIMULATE
inputs = [nd for nd in GetLeaves(populations[2])[0]]
for i in range(num['steps']):

    image = SEM_input.draw_image(SEM_input.SEM_input_config['centers'][i%4],SEM_input.SEM_input_config)

    # prepare input population firing rates
    for j in range(SEM_input.SEM_input_config['image_width']):
        for k in range(SEM_input.SEM_input_config['image_width']):
            this_rate = SEM_input.SEM_input_config['input_on_rate'] if (image[j][k] > 0.0) else SEM_input.SEM_input_config['input_off_rate']
            SetStatus([inputs[j*SEM_input.SEM_input_config['image_width']+k]],{'rate': this_rate})
            #SetStatus([inputs[2*j*SEM_input.SEM_input_config['image_width']+k*2+1]],{'rate': SEM_input.SEM_input_config['input_on_rate'] if (image[j][k]<1.0) else SEM_input.SEM_input_config['input_off_rate']})

    print "[Running simulation step %d]" % (i)
    Simulate(tshow)

    for j in range(SEM_input.SEM_input_config['image_width']):
        for k in range(SEM_input.SEM_input_config['image_width']):
            SetStatus([inputs[j*SEM_input.SEM_input_config['image_width']+k]],{'rate': 0.0})
            #SetStatus([inputs[2*j*SEM_input.SEM_input_config['image_width']+k*2+1]],{'rate': 0.0})

    Simulate(tpaus)

    if i%num['steps_rate_average']==0 and i>0 and with_homeostatis:
        for neuron in range(num['l0_exc_neurons']):
            events_ex = GetStatus([exc_spikedetectors[neuron]],'n_events')[0]
            rate = (events_ex-last_events[neuron])/((tshow+tpaus)*num['steps_rate_average']*1e-3)
            last_events[neuron] = events_ex
            g_L = 5.0/(1+(rate-20.0)/100.0)
            print rate,g_L
            SetStatus([GetLeaves(populations[0])[0][neuron]],{'tau_m':g_L})
    #        #if rate < 15.0:
    #        #    SetStatus([GetLeaves(populations[0])[0][neuron]],{'g_L':5.0})
    #        #elif rate > 35.0:
    #        #    SetStatus([GetLeaves(populations[0])[0][neuron]],{'g_L':15.0})
    #        #else:                                              
    #        #    SetStatus([GetLeaves(populations[0])[0][neuron]],{'g_L':10.0})

    if i%100==0 and i>0:
        dump_weights(populations[3],'post')

if with_plot_weights:
    plot_weights(populations[3],2)
    plot_weights(populations[3],3)
    plot_weights(populations[3],4)
    plot_weights(populations[3],5)
    plt.show()

dump_weights(populations[3],'post')

# PRINT
#PrintNetwork(depth=2)
