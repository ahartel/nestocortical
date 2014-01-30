import numpy as np
import scipy.io as sio
import sys, socket, png, pickle

from pyNN.utility import get_script_args
from pyNN.random import NumpyRNG

seed = 764756387
tstop = 50.0 # ms
input_rate = 50.0 # Hz
cell_params = {'tau_refrac': 2.0,  # ms
               'v_thresh':  -50.0, # mV
               'tau_syn_E':  2.0,  # ms
               'tau_syn_I':  2.0}  # ms

num = {}
#num['nodes'] = 50
#num['neighbours'] = 4
num['l0_exc_neurons'] = 80
num['l1_exc_neurons'] = 20
num['l0_inh_neurons'] = 20
num['l1_inh_neurons'] = 5
num['inputs'] = 1024*3
#num['conns_per_input'] = 5
num['steps'] = 5000

basepath = '/home/ahartel/data/SVHN/train'

def setupNetwork():
    node = pynn.setup(timestep=0.1, min_delay=1.0, max_delay=1.0, debug=True, quit_on_end=False)
    print "Process with rank %d running on %s" % (node, socket.gethostname())


    rng = NumpyRNG(seed=seed, parallel_safe=True)

    #n_spikes = int(2*tstop*input_rate/1000.0)
    #spike_times = numpy.add.accumulate(rng.next(n_spikes, 'exponential',
    #                       [1000.0/input_rate], mask_local=False))

    print "[%d] Creating populations" % node
    # 1) excitatory populations
    l0_exc_population = pynn.Population(num['l0_exc_neurons'], pynn.IF_curr_exp, cell_params, label="exc0")
    #l0_exc_population.record()
    l1_exc_population = pynn.Population(num['l1_exc_neurons'], pynn.IF_curr_exp, cell_params, label="exc1")
    #l1_exc_population.record()

    # 2) inhibitory population
    l0_inh_population = pynn.Population(num['l0_inh_neurons'], pynn.IF_curr_exp, cell_params, label="inh0")
    #l0_inh_population.record()
    l1_inh_population = pynn.Population(num['l1_inh_neurons'], pynn.IF_curr_exp, cell_params, label="inh1")
    #l1_inh_population.record()

    # 3) connect exc. populations to neiboughring inh. population
    inh_connector = pynn.FixedProbabilityConnector(0.6,weights=1.0)
    l0_exc_inh_projection = pynn.Projection(l0_exc_population,l0_inh_population,inh_connector)
    l1_exc_inh_projection = pynn.Projection(l1_exc_population,l1_inh_population,inh_connector)

    exc_connector = pynn.FixedProbabilityConnector(0.6,weights=1.0,allow_self_connections=False)
    l0_exc_exc_projection = pynn.Projection(l0_exc_population,l0_exc_population,exc_connector)
    l1_exc_exc_projection = pynn.Projection(l1_exc_population,l1_exc_population,exc_connector)

    #for i in range(num['nodes']):
    #    exc_inh_projections.append(Projection(exc_populations[i],inh_population,inh_connector))
    #    for j in range(i-num['neighbours'],i+num['neighbours']+1):
    #        if j != i:
    #            exc_connector = OneToOneConnector(weights=1.0/abs(j-i))

    #            if j<0:
    #                j+=num['nodes']
    #            if j> num['nodes']-1:
    #                j-=num['nodes']

    #            exc_exc_projections.append(Projection(exc_populations[i],exc_populations[j],exc_connector))

    # 4) connect inh. populations to exc. populations
    connector = pynn.FixedProbabilityConnector(0.6,weights=-1.3)
    l0_inh_exc_projection = pynn.Projection(l0_inh_population, l0_exc_population,connector,target="inhibitory")
    l1_inh_exc_projection = pynn.Projection(l1_inh_population, l1_exc_population,connector,target="inhibitory")

    # 5)
    input_population = pynn.Population(num['inputs'], pynn.SpikeSourcePoisson, {'rate': input_rate }, label="input")
    #input_population.record()

    # 6)
    stdp_model = pynn.STDPMechanism(
        timing_dependence=pynn.SpikePairRule(tau_plus=20.0, tau_minus=20.0),
        weight_dependence=pynn.AdditiveWeightDependence(w_min=0, w_max=1.0,
        A_plus=0.01, A_minus=0.012)
    )

    connector = pynn.AllToAllConnector(weights=pynn.RandomDistribution(distribution='uniform',parameters=[0.3,1.0],rng=rng))
    input_projection = pynn.Projection(input_population, l0_exc_population, connector, rng=rng, synapse_dynamics=pynn.SynapseDynamics(slow=stdp_model))
    #connector = pynn.FixedProbabilityConnector(0.6, weights=1.0)
    l1_projection = pynn.Projection(l0_exc_population, l1_exc_population, connector, rng=rng, synapse_dynamics=pynn.SynapseDynamics(slow=stdp_model))

    return node,l0_exc_population,l1_exc_population,l0_inh_population,l1_inh_population,input_population,input_projection,l1_projection

if __name__ == "__main__":
    simulator_name = 'nest'
    try:
        simulator_name = get_script_args(1)[0]
    except Exception:
        print "Using default simulator nest"
    exec("import pyNN.%s as pynn" % simulator_name)

    node,l0_exc_population,l1_exc_population,l0_inh_population,l1_inh_population,input_population,input_projection,l1_projection = setupNetwork()

    file_stem = "Results/svhn_wta_np%d_%s" % (pynn.num_processes(), simulator_name)
    #projection.saveConnections('%s.conn' % file_stem)

    # save initial weights
    with open("%s_initial_weights.wgt"%(file_stem,),'wb') as f:
        pickle.dump([input_projection.getWeights(format='array'),l1_projection.getWeights(format='array')],f)

    # input population views
    input_pop_views = []
    for i in range(num['inputs']):
        input_pop_views.append(pynn.PopulationView(input_population,[i]))

    # read matlab file with image data and generate input firing rates
    mat = sio.loadmat(basepath+'/train_32x32.mat')
    data = np.array(mat['X'])
    stop=num['steps']
    for i in range(len(mat['y'])):
        stop-=1
        if stop==0:
            break
        cnt = 0
        # prepare input population firing rates
        png_data = []
        for row in data[:,:,:,i]:
            data_set = ()
            for pixel in row:
                #total=0
                for value in pixel:
                    data_set += (value,)
                    #total+=value
                    input_pop_views[cnt].set('rate',input_rate/(256)*value)
                    cnt+=1
            png_data.append(data_set)

        with open(basepath+'/generated/'+str(i)+'.png','wb') as f:
            w = png.Writer(32,32)
            w.write(f,png_data)

        print "[%d] Running simulation step %d" % (node,stop)
        pynn.run(tstop)

    # save final weights
    with open("%s_final_weights.wgt"%(file_stem,),'wb') as f:
        pickle.dump([input_projection.getWeights(format='array'),l1_projection.getWeights(format='array')],f)

    print "[%d] Writing spikes to disk" % node
    #l0_exc_population.printSpikes('%s_exc_0.ras' % (file_stem,))
    #l1_exc_population.printSpikes('%s_exc_1.ras' % (file_stem,))
    #l0_inh_population.printSpikes('%s_inh_0.ras' % (file_stem,))
    #l1_inh_population.printSpikes('%s_inh_1.ras' % (file_stem,))
    #input_population.printSpikes('%s_input.ras' % (file_stem,))
    with open('%s_labels.txt'%(file_stem,),'w') as f:
        for value in mat['y'][0:num['steps']-1]:
            f.write('%s\n'%(value[0]))

    print "[%d] Finishing" % node
    pynn.end()
    print "[%d] Done" % node

