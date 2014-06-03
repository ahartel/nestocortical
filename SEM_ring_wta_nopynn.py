from nest import *
import nest.topology as tp
import SEM_input
import nest.voltage_trace as vt
import nest.raster_plot as rp
import matplotlib.pyplot as plt

#t_sim = 10000.0
#n_ex = 16000
#n_in = 4000
#r_ex = 5.0
#r_in = 12.5
#epsc = 45.0
#ipsc = -45.0
#
#neuron = Create("aeif_cond_exp")
#noise = Create("poisson_generator",2)
#voltmeter = Create("voltmeter")
#spikedetector = Create("spike_detector")
#
#SetStatus(noise, [{"rate": n_ex*r_ex}, {"rate": n_in*r_in}])
#SetStatus(voltmeter, {"interval": 10.0, "withgid": True})
#
#ConvergentConnect(noise, neuron, [epsc, ipsc], 1.0)
#Connect(voltmeter, neuron)
#Connect(neuron, spikedetector)
#
#Simulate(1000)
#
#vt.from_device(voltmeter)
#plt.show()


seed = 764756387
tshow = 40.0 # ms
tpaus = 10.0
input_rate = 40.0 # Hz
cell_params_lif = {
               'V_th'  :-50.0,  # mV
               'g_L'     : 10.0,  # ms 
               'tau_syn_ex' :  2.5,  # ms
               'tau_syn_in' :  5.0,  # ms
            }

# values taken from Naud et al. 2008
cell_params_adex = {
                'C_m'        :  0.2,  # nF
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
                #'V_reset_'   :-46.0,  # mV
                'gsl_error_tol': 1e-8,
    }

print GetDefaults('iaf_cond_exp')
print GetDefaults('aeif_cond_exp')
#SetDefaults('iaf_cond_exp',cell_params_lif)
SetDefaults('aeif_cond_exp',{'gsl_error_tol':1e-7})

num = {}
num['l0_exc_neurons'] = 64
num['l0_exc_maxneighbors'] = 4
num['l1_exc_neurons'] = 4
num['l1_exc_maxneighbors'] = 4
num['l0_l1_maxneighbors'] = 4
num['l0_inh_neurons'] = 4
num['l1_inh_neurons'] = 5
num['inputs'] = SEM_input.SEM_input_config['num_inputs']
num['inputs_maxneighbors'] = 4
num['steps'] = 100
num['steps_firing_rate_average'] = 10


# input -> exc0
w_inp_exc0_peak = 0.0002
sigma_inp_exc0 = 0.2
w_inp_exc0_max = 0.0045

# exc0 -> exc1
sigma_exc0_exc1 = 4.
w_exc0_exc1_peak = 0.005
w_exc0_exc1_max = 0.005

# exc0 -> inh0
p_exc0_inh0 = 1.0
w_exc0_inh0 = 0.001

# exc0 -> exc0
sigma_exc0_exc0 = 0.1
w_exc0_exc0_max = 0.001

# exc1 -> exc1
sigma_exc1_exc1 = 7.
w_exc1_exc1_max = 0.001

# exc1 -> inh1
p_exc1_inh1 = 1.0
w_exc1_inh1 = 0.02

# inh0 -> exc0
p_inh0_exc0 = 1.0
w_inh0_exc0 = -0.01

# inh1 -> exc1
p_inh1_exc1 = 1.0
w_inh1_exc1 = 0.1


def setup_network():

    print "[ Creating excitatory population ]"
    # 1) create excitatory populations
    l0_exc_population =  tp.CreateLayer ({
                                'rows' : 1 ,
                                'columns' : num['l0_exc_neurons'],
                                #'extent' : [ float(num['l0_exc_neurons']), 1.  ],
                                'elements' : 'aeif_cond_exp',
                                'edge_wrap' : True } )

    #tp.PlotLayer(l0_exc_population, nodesize=50)

    print "[ Creating inhibitory population ]"
    # 2) create inhibitory population
    l0_inh_population =  tp.CreateLayer ({
                                'rows' : 1,
                                'columns' : num['l0_inh_neurons'],
                                #'extent' : [ float(num['l0_inh_neurons']), 1.  ] ,
                                'elements' : 'iaf_cond_exp',
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
                'kernel':p_exc0_inh0,
                'synapse_model': 'exc_inh'
            }
    tp.ConnectLayers(l0_exc_population,l0_inh_population,l0_exc_inh_dict)
    #pynn.FixedProbabilityConnector(p_exc0_inh0,weights=w_exc0_inh0)
    #l0_exc_inh_projection = pynn.Projection(l0_exc_population,l0_inh_population,inh_connector)

    print "[ Projecting excitatory -> excitatory population ]"
    # 4) exc -> exc
    # Since these connections are distance-dependent, we can use topological connections here
    CopyModel('static_synapse','exc_exc',{'weight':w_exc0_exc0_max})
    l0_exc_exc_dict = {
                'connection_type': 'convergent',
                'mask': {
                    'rectangular': {
                        'lower_left': [-0.5,-0.5],
                        'upper_right':[0.5,0.5]
                    }
                },
                'synapse_model': 'exc_exc',
                'weights': {
                    'gaussian': {'p_center': 1., 'sigma': sigma_exc0_exc0}
                }
            }
    tp.ConnectLayers(l0_exc_population,l0_exc_population,l0_exc_exc_dict)
    #exc_connector = pynn.AllToAllConnector(weights=0.0)
    #l0_exc_exc_projection = pynn.Projection(l0_exc_population,l0_exc_population,exc_connector)
    #exc0_exc0_weights = l0_exc_exc_projection.getWeights()

    #exc0_exc0_weights = connect_gauss(num['l0_exc_neurons'],num['l0_exc_neurons'],sigma_exc0_exc0,w_exc0_exc0_max,num['l0_exc_maxneighbors'],exc0_exc0_weights,True)

    #l0_exc_exc_projection.setWeights(exc0_exc0_weights)

    print "[ Projecting inhibitory -> excitatory population ]"
    # 5) inh -> exc
    CopyModel('static_synapse','inh_exc', {'weight':w_inh0_exc0})
    l0_inh_exc_dict = {
                'connection_type' : 'convergent',
                'mask': {
                    'rectangular': {
                        'lower_left': [-0.5,-0.5],
                        'upper_right':[0.5,0.5]
                    }
                },
                'kernel':p_inh0_exc0,
                'synapse_model': 'inh_exc'
            }
    tp.ConnectLayers(l0_inh_population,l0_exc_population,l0_inh_exc_dict)


    print "[ Creating input population ]"
    # 6) create input population
    CopyModel('poisson_generator','input_model',{'rate':50.0})
    input_population =  tp.CreateLayer ({
                                'rows' : 1 ,
                                'columns' : num['inputs'],
                                #'extent' : [ float(num['l0_exc_neurons']), 1.  ],
                                'elements' : 'input_model',
                                'edge_wrap' : True } )

    parrot_population =  tp.CreateLayer ({
                                'rows' : 1 ,
                                'columns' : num['inputs'],
                                #'extent' : [ float(num['l0_exc_neurons']), 1.  ],
                                'elements' : 'parrot_neuron',
                                'edge_wrap' : True } )

    print "[ Projecting input -> excitatory population ]"
    # 7) input -> exc
    CopyModel('static_synapse','input_parrot', {'weight': 1.0})
    #CopyModel('stdp_synapse','parrot_exc', {'weight':w_inp_exc0_peak,'alpha':0.012,'Wmax':w_inp_exc0_max})
    CopyModel('static_synapse','parrot_exc', {'weight':w_inp_exc0_peak})
    input_parrot_dict = {
                'connection_type' : 'convergent',
                'mask': {
                    'rectangular': {
                        'lower_left': [-0.5,-0.5],
                        'upper_right':[0.5,0.5]
                    }
                },
                'synapse_model': 'input_parrot'
            }
    parrot_exc_dict = {
                'connection_type' : 'convergent',
                'mask': {
                    'rectangular': {
                        'lower_left': [-0.05,-0.5],
                        'upper_right':[0.05,0.5]
                    }
                },
                'weights': {'gaussian': {'p_center':1.,'sigma':sigma_inp_exc0}},
                'synapse_model': 'parrot_exc'
            }
    tp.ConnectLayers(input_population,parrot_population,input_parrot_dict)
    tp.ConnectLayers(parrot_population,l0_exc_population,parrot_exc_dict)

    #stdp_model = pynn.STDPMechanism(
    #    timing_dependence=pynn.SpikePairRule(tau_plus=10.0, tau_minus=15.0),
    #    weight_dependence=pynn.AdditiveWeightDependence(w_min=0, w_max=w_inp_exc0_max,
    #    A_plus=0.012, A_minus=0.012)
    #)

    #connector = pynn.AllToAllConnector(weights=0.0)
    #input_projection = pynn.Projection(
    #        input_population,
    #        l0_exc_population,
    #        connector,
    #        rng=rng,
    #        synapse_dynamics=pynn.SynapseDynamics(slow=stdp_model)
    #    )

    #input_weights = input_projection.getWeights()

    #print "[%d] Creating input projections" % node
    #input_weights = connect_gauss(num['inputs'],num['l0_exc_neurons'],sigma_inp_exc0,w_inp_exc0_peak,num['inputs_maxneighbors'],input_weights,False)

    #input_projection.setWeights(input_weights)

    return l0_exc_population,l0_inh_population,input_population#,l1_projection

# CREATE
populations = setup_network()
# PRINT
PrintNetwork(depth=2)
#print GetStatus(populations[0])
#print GetStatus(populations[2])
#tgts = GetStatus(FindConnections(tp.GetElement(populations[0],[0,0])))
#print tgts
#tgts = GetStatus(FindConnections(tp.GetElement(populations[0],[1,0])))
#print tgts
#connPlot(populations[2],'input_model','aeif_cond_exp','input_exc','title')

# CONNECT READOUTS
#connect_readouts(l0_exc_population,l0_inh_population,input_population)
voltmeters = Create('voltmeter',2)
spikedetectors = Create('spike_detector',3)
for n,pop in enumerate(populations):
    tgts = [nd for nd in GetLeaves(populations[n])[0]] 
    ConvergentConnect(tgts,[spikedetectors[n]])
    # voltmeters only for non-inputs
    if n < 2:
        DivergentConnect([voltmeters[n]],[tgts[0]])

Simulate(50)
vt.from_device([voltmeters[0]])
vt.from_device([voltmeters[1]])
rp.from_device([spikedetectors[0]])
#rp.from_device([spikedetectors[1]])
rp.from_device([spikedetectors[2]])
plt.show()
#FindConnections(l0_exc_population)
