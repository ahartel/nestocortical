"""
Simple network with a 1D population of poisson spike sources
projecting to a 2D population of IF_curr_exp neurons.

Andreas Hartel, KIP, UHEI
January 2014

1) Create 'num['nodes']' excitatory populations
   (Each population contains 'num['exc_neurons']' neurons (start with 1 and increase if more strength is necessary))
2) Create 'num['nodes']' inhibitory populations
   (Each population contains 'num['inh_neurons']' neurons (start with 1 and increase if more strength is necessary))
3) Connect each excitatory to exactly one inhibitory population
4) Connect each inhibitory population to all excitatory population except the one projecting to it
5) Generate 'num['inputs']' input spike sources
6) Randomly connect each input source to 'num['conns_per_input']' excitatory populations with STDP synapses
7) Run

"""

import socket

from pyNN.utility import get_script_args

simulator_name = 'nest'
try:
	simulator_name = get_script_args(1)[0]
except Exception:
	print "Using default simulator nest"

exec("from pyNN.%s import *" % simulator_name)

from pyNN.random import NumpyRNG

seed = 764756387
tstop = 3000.0 # ms
input_rate = 100.0 # Hz
cell_params = {'tau_refrac': 2.0,  # ms
               'v_thresh':  -50.0, # mV
               'tau_syn_E':  2.0,  # ms
               'tau_syn_I':  2.0}  # ms

num = {}
num['nodes'] = 50
num['neighbours'] = 4
num['exc_neurons'] = 10
num['inh_neurons'] = 30
num['inputs'] = 200
num['conns_per_input'] = 5

if __name__ == "__main__":
	node = setup(timestep=0.1, min_delay=1.0, max_delay=1.0, debug=True, quit_on_end=False)
	print "Process with rank %d running on %s" % (node, socket.gethostname())


	rng = NumpyRNG(seed=seed, parallel_safe=True)

	#n_spikes = int(2*tstop*input_rate/1000.0)
	#spike_times = numpy.add.accumulate(rng.next(n_spikes, 'exponential',
	#					    [1000.0/input_rate], mask_local=False))

	print "[%d] Creating populations" % node
	# 1) excitatory populations
	exc_populations = []
	for i in range(num['nodes']):
		exc_populations.append(Population(num['exc_neurons'], IF_curr_exp, cell_params, label="exc"+str(i)))
		exc_populations[i].record()

	# 2) inhibitory population
	inh_population = Population(num['inh_neurons'], IF_curr_exp, cell_params, label="inh")
	inh_population.record()

	# 3) connect exc. populations to neiboughring inh. population
	exc_inh_projections = []
	exc_exc_projections = []
	inh_connector = FixedProbabilityConnector(0.6,weights=1.0)
	for i in range(num['nodes']):
		exc_inh_projections.append(Projection(exc_populations[i],inh_population,inh_connector))
		for j in range(i-num['neighbours'],i+num['neighbours']+1):
			if j != i:
				exc_connector = OneToOneConnector(weights=1.0/abs(j-i))

				if j<0:
					j+=num['nodes']
				if j> num['nodes']-1:
					j-=num['nodes']

				exc_exc_projections.append(Projection(exc_populations[i],exc_populations[j],exc_connector))

	# 4) connect inh. populations to all other exc. populations
	connector = FixedProbabilityConnector(0.6,weights=-1.0)
	for i in range(num['nodes']):
		Projection(inh_population, exc_populations[i],connector,target="inhibitory")

	# 5)
	input_populations = []
	for i in range(num['inputs']):
		#input_populations.append(Population(1, SpikeSourceArray, {'spike_times': spike_times }, label="input"))
		input_populations.append(Population(1, SpikeSourcePoisson, {'rate': input_rate }, label="input"))
		input_populations[i].record()

	# 6)
	stdp_model = STDPMechanism(
		timing_dependence=SpikePairRule(tau_plus=20.0, tau_minus=20.0),
		weight_dependence=AdditiveWeightDependence(w_min=0, w_max=1.0,
		A_plus=0.01, A_minus=0.012)
	)

	connector = FixedProbabilityConnector(0.7, weights=1.0)
	for i in range(num['inputs']):
		for j in range(num['nodes']):
			projection = Projection(input_populations[i], exc_populations[j], connector, rng=rng, synapse_dynamics=SynapseDynamics(slow=stdp_model))


	file_stem = "Results/wta_np%d_%s" % (num_processes(), simulator_name)
	#projection.saveConnections('%s.conn' % file_stem)

	print "[%d] Running simulation" % node
	run(tstop)

	print "[%d] Writing spikes to disk" % node
	for i in range(num['nodes']):
		exc_populations[i].printSpikes('%s_output_%d.ras' % (file_stem,i))
	inh_population.printSpikes('%s_inhibit.ras' % (file_stem,))
	for i in range(num['inputs']):
		input_populations[i].printSpikes('%s_input_%d.ras' % (file_stem,i))

	print "[%d] Finishing" % node
	end()
	print "[%d] Done" % node
