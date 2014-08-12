"""
Simple network implementing a soft-WTA with LIF neurons

Andreas Hartel, KIP, UHEI
January 2014

1) Create num['exc_neurons'] excitatory neurons
2) Create num['inh_neurons'] inhibitory neurons
3) Connect the excitatory neuron to the inhibitory population
4) Connect the inhibitory population to the excitatory population
5) Generate num['inputs'] input spike sources
6) Randomly connect each input source to all excitatory neurons
7) Run

"""

import socket

from pyNN.utility import get_script_args

simulator_name = 'nest'

from pyNN.random import NumpyRNG

seed = 764756387
tstop = 3000.0 # ms
input_rate = 10.0 # Hz
cell_params = {'tau_refrac': 2.0,  # ms
               'v_thresh':  -50.0, # mV
               'v_rest'  :  -65.0, # mV
               'tau_syn_E':  2.0,  # ms
               'tau_syn_I':  2.0   # ms
}

exc_exc_sigma = 7.

num = {}
num['max_neighbors'] = int(3*exc_exc_sigma)
num['exc_neurons'] = 50
num['inh_neurons'] = 16
num['stims_per_neuron'] = 5
num['bump_max_neighbor'] = 9

if __name__ == "__main__":
    try:
        simulator_name = get_script_args(1)[0]
    except Exception:
        print "Using default simulator nest"

    exec("from pyNN.%s import *" % simulator_name)

    node = setup(timestep=0.1, min_delay=1.0, max_delay=1.0, debug=True, quit_on_end=False)
    print "Process with rank %d running on %s" % (node, socket.gethostname())

    rng = NumpyRNG(seed=seed, parallel_safe=True)

    #n_spikes = int(2*tstop*input_rate/1000.0)
    #spike_times = numpy.add.accumulate(rng.next(n_spikes, 'exponential',
    #                       [1000.0/input_rate], mask_local=False))

    print "[%d] Creating populations" % node
    # 1) excitatory populations
    exc_population = Population(num['exc_neurons'], IF_cond_alpha, cell_params, label="exc")
    exc_population.record()

    # 2) inhibitory population
    inh_population = Population(num['inh_neurons'], IF_cond_alpha, cell_params, label="inh")
    inh_population.record()

    # 3) connect exc. populations to neiboughring inh. population
    exc_inh_connector = FixedProbabilityConnector(0.6,weights=0.007,allow_self_connections=False)
    exc_inh_projection = Projection(exc_population,inh_population,exc_inh_connector)

    avoidSelfConn = True
    # ring self stimulation to neighbors
    for i in range(num['exc_neurons']):
        for d in range(-num['max_neighbors'], num['max_neighbors'] + 1):
            j = i + d
            k = j%num['exc_neurons']
            w = 0.01
            if exc_exc_sigma > 0.:
                w *= numpy.exp(-d**2/exc_exc_sigma**2) # (cut) Gaussian around stimulated position
            if not (avoidSelfConn and i==k):
                connect(exc_population.cell[i], exc_population.cell[k], weight=w, synapse_type='excitatory')
                #TODO: can be done with PopViews
                #pynn.Projection(ne[i], ne[k], method=pynn.AllToAllConnector(weights=minExcWeight * w), target='excitatory')
    

    # 4) connect inh. populations to all other exc. populations
    inh_exc_connector = FixedProbabilityConnector(1.0,weights=0.024)
    inh_exc_projection = Projection(inh_population, exc_population,inh_exc_connector,target="inhibitory")

    # 5)
    #input_population = Population(num['inputs'], SpikeSourcePoisson, {'rate': input_rate }, label="input")
    #input_population.record()
    stim = None

    inputBumpPos = [12, 37]
    inputBumpFreqs = [0., 50.]
    minInhWeight = 0.004
    minExcWeight = 0.001
    w1, w2 = 12,12
    inputBumpWeights= [minExcWeight * w1, minExcWeight * w2]
    duration = 1000.0 # ms

    inputParameters = {
            'rate'      : 1.0,              # Hz
            'start'     : 0.0,              # ms
            'duration'  : duration          # ms
     }   
    inputBumpOnset= [0., 0.]#duration/2.]
    bumpSigma = 3.
    stimCollector = []#
    p_connect = 1.

    # stimulus
    for i in range(len(inputBumpPos)):
        print '--',i
        for d in range(-num['bump_max_neighbor'], num['bump_max_neighbor'],  + 1):
            j = inputBumpPos[i] + d
            k = j%num['exc_neurons']
            w = inputBumpWeights[i]
            if bumpSigma > 0.:
                w *= numpy.exp(-(d**2)/(bumpSigma**2))
            ip = dict(inputParameters)
            ip['rate'] = inputBumpFreqs[i]
            ip['start'] = inputBumpOnset[i]
            stim = Population(num['stims_per_neuron'], SpikeSourcePoisson, ip)
            stim.record()
            stimCollector.append(stim)
            for n in range(num['stims_per_neuron']):
                if numpy.random.random() < p_connect:
                    print w
                    connect(stim.cell[n], exc_population.cell[k], weight=w, synapse_type='excitatory')
            #pynn.Projection(stim, ne[k], method=pynn.AllToAllConnector(weights=w), tar    get='excitatory')

    #center=30
    #PopulationView(input_population,[center-3]).set('rate',70)
    #PopulationView(input_population,[center-2]).set('rate',80)
    #PopulationView(input_population,[center-1]).set('rate',90)
    #PopulationView(input_population,[center]).set('rate',100)
    #PopulationView(input_population,[center+1]).set('rate',90)
    #PopulationView(input_population,[center+2]).set('rate',80)
    #PopulationView(input_population,[center+3]).set('rate',70)

    # 6)
    #stdp_model = STDPMechanism(
    #    timing_dependence=SpikePairRule(tau_plus=20.0, tau_minus=20.0),
    #    weight_dependence=AdditiveWeightDependence(w_min=0, w_max=1.0,
    #    A_plus=0.01, A_minus=0.012)
    #)

    #connector = AllToAllConnector(weights=RandomDistribution(distribution='uniform',parameters=[0.5,1.5],rng=rng))
    #connector = FixedProbabilityConnector(0.6,weights=RandomDistribution(distribution='uniform',parameters=[0.3,1.0],rng=rng))
    #input_projection = Projection(input_population, exc_population, connector, rng=rng)#, synapse_dynamics=SynapseDynamics(slow=stdp_model))

    # 7)
    file_stem = "Results/wta_np%d_%s" % (num_processes(), simulator_name)
    #projection.saveConnections('%s.conn' % file_stem)

    print "[%d] Running simulation" % node
    run(tstop)

    print "[%d] Writing spikes to disk" % node
    exc_population.printSpikes('%s_output.ras' % (file_stem,))
    inh_population.printSpikes('%s_inhibit.ras' % (file_stem,))
    for i,stim in enumerate(stimCollector):
        stim.printSpikes('%s_input_%s.ras' % (file_stem,i))

    print "[%d] Finishing" % node
    end()
    print "[%d] Done" % node
