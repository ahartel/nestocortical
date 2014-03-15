import numpy as np
import scipy.io as sio
import sys, socket, png, pickle

from pyNN.utility import get_script_args
from pyNN.random import NumpyRNG

seed = 764756387
tstop = 50.0 # ms
input_rate = 40.0 # Hz
cell_params = {'tau_refrac':  2.0,  # ms
               'v_thresh'  :-50.0,  # mV
               'tau_m'     : 10.0,  # ms 
               'tau_syn_E' :  2.5,  # ms
               'tau_syn_I' :  5.0}  # ms

num = {}
#num['nodes'] = 50
#num['neighbours'] = 4
num['l0_exc_neurons'] = 50
num['l1_exc_neurons'] = 10
num['l0_inh_neurons'] = 16
num['l1_inh_neurons'] = 3
num['inputs'] = 1024*3
num['steps'] = 50

#p_inp_exc0 = 0.01
#w_inp_exc0 = 0.00001

w_inp_exc0_max = 0.0004
w_exc0_exc1_max = 0.003

p_exc0_inh0 = 0.6
w_exc0_inh0 = 0.005

p_exc0_exc0 = 0.5
w_exc0_exc0 = 0.001

p_exc1_inh1 = 1.0
w_exc1_inh1 = 0.02

p_inh0_exc0 = 0.6
w_inh0_exc0 = 0.01

p_inh1_exc1 = 1.0
w_inh1_exc1 = 0.1

basepath = '/home/ahartel/data/SVHN/train'

def setupNetwork():
    node = pynn.setup(timestep=0.1, min_delay=1.0, max_delay=1.0, debug=True, quit_on_end=False)
    print "Process with rank %d running on %s" % (node, socket.gethostname())

    rng = NumpyRNG(seed=seed, parallel_safe=True)

    print "[%d] Creating populations" % node
    # 1) create excitatory populations
    l0_exc_population = pynn.Population(num['l0_exc_neurons'], pynn.IF_cond_exp, cell_params, label="exc0")
    l0_exc_population.record()
    #l0_exc_population.record_v()
    l1_exc_population = pynn.Population(num['l1_exc_neurons'], pynn.IF_cond_exp, cell_params, label="exc1")
    l1_exc_population.record()

    # 2) create inhibitory population
    l0_inh_population = pynn.Population(num['l0_inh_neurons'], pynn.IF_cond_exp, cell_params, label="inh0")
    l0_inh_population.record()
    l1_inh_population = pynn.Population(num['l1_inh_neurons'], pynn.IF_cond_exp, cell_params, label="inh1")
    l1_inh_population.record()

    # 3) exc0 -> inh0
    inh_connector = pynn.FixedProbabilityConnector(p_exc0_inh0,weights=w_exc0_inh0)
    l0_exc_inh_projection = pynn.Projection(l0_exc_population,l0_inh_population,inh_connector)

    # 4) exc1 -> inh1
    inh_connector = pynn.FixedProbabilityConnector(p_exc1_inh1,weights=w_exc1_inh1)
    l1_exc_inh_projection = pynn.Projection(l1_exc_population,l1_inh_population,inh_connector)

    # 5) exc0 -> exc0
    exc_connector = pynn.FixedProbabilityConnector(p_exc0_exc0,weights=w_exc0_exc0,allow_self_connections=False)
    l0_exc_exc_projection = pynn.Projection(l0_exc_population,l0_exc_population,exc_connector)

    # 6) exc1 -> exc1
    #l1_exc_exc_projection = pynn.Projection(l1_exc_population,l1_exc_population,exc_connector)

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

    # 7) inh0 -> exc0
    connector = pynn.FixedProbabilityConnector(p_inh0_exc0,weights=w_inh0_exc0)
    l0_inh_exc_projection = pynn.Projection(
            l0_inh_population,
            l0_exc_population,
            connector,
            target="inhibitory"
        )

    # 8) inh1 -> exc1
    connector = pynn.FixedProbabilityConnector(p_inh1_exc1,weights=w_inh1_exc1)
    l1_inh_exc_projection = pynn.Projection(
            l1_inh_population,
            l1_exc_population,
            connector,
            target="inhibitory"
        )

    # 9) create input population
    input_population = pynn.Population(
            num['inputs'],
            pynn.SpikeSourcePoisson,
            {
                'rate': input_rate
            },
            label="input"
        )
    input_population.record()

    # 10) input -> exc0
    stdp_model = pynn.STDPMechanism(
        timing_dependence=pynn.SpikePairRule(tau_plus=20.0, tau_minus=20.0),
        weight_dependence=pynn.AdditiveWeightDependence(w_min=0, w_max=w_inp_exc0_max,
        A_plus=0.01, A_minus=0.012)
    )
    connector = pynn.AllToAllConnector(
            weights=pynn.RandomDistribution(
                distribution='uniform',
                parameters=[0.00,w_inp_exc0_max],
                rng=rng
            )
        )
    #connector = pynn.FixedProbabilityConnector(p_inp_exc0,weights=w_inp_exc0)
    input_projection = pynn.Projection(
            input_population,
            l0_exc_population,
            connector,
            rng=rng,
            #synapse_dynamics=pynn.SynapseDynamics(slow=stdp_model)
        )

    # 11) exc0 -> exc1
    stdp_model = pynn.STDPMechanism(
        timing_dependence=pynn.SpikePairRule(tau_plus=20.0, tau_minus=20.0),
        weight_dependence=pynn.AdditiveWeightDependence(w_min=0, w_max=w_exc0_exc1_max,
        A_plus=0.01, A_minus=0.012)
    )
    connector = pynn.AllToAllConnector(
            weights=pynn.RandomDistribution(
                distribution='uniform',
                parameters=[0.00,w_exc0_exc1_max],
                rng=rng
            )
        )
    #connector = pynn.FixedProbabilityConnector(0.05, weights=0.01)
    l1_projection = pynn.Projection(
            l0_exc_population,
            l1_exc_population,
            connector,
            rng=rng,
            #synapse_dynamics=pynn.SynapseDynamics(slow=stdp_model)
        )

    return node,l0_exc_population,l1_exc_population,l0_inh_population,l1_inh_population,input_population,input_projection,l1_projection


#########
# main
#########
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
    input_weights = input_projection.getWeights(format='array')
    l1_weights = l1_projection.getWeights(format='array')
    with open("%s_initial_weights.wgt"%(file_stem,),'wb') as f:
        pickle.dump([input_weights,l1_weights],f)

    # input population views
    input_pop_views = []
    for i in range(num['inputs']):
        input_pop_views.append(pynn.PopulationView(input_population,[i]))

    afferents = [0.0 for i in range(num['inputs'])]

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
                    #print input_weights[cnt]
                    cnt+=1
            png_data.append(data_set)

        # write out a png for debugging
        with open(basepath+'/generated/'+str(i)+'.png','wb') as f:
            w = png.Writer(32,32)
            w.write(f,png_data)

        print "[%d] Running simulation step %d" % (node,stop)
        pynn.run(tstop)

    # save final weights
    with open("%s_final_weights.wgt"%(file_stem,),'wb') as f:
        pickle.dump([input_projection.getWeights(format='array'),l1_projection.getWeights(format='array')],f)

    print "[%d] Writing spikes to disk" % node
    l0_exc_population.printSpikes('%s_exc_0.ras' % (file_stem,))
    l1_exc_population.printSpikes('%s_exc_1.ras' % (file_stem,))
    l0_inh_population.printSpikes('%s_inh_0.ras' % (file_stem,))
    l1_inh_population.printSpikes('%s_inh_1.ras' % (file_stem,))
    input_population.printSpikes('%s_input.ras' % (file_stem,))
    with open('%s_labels.txt'%(file_stem,),'w') as f:
        for value in mat['y'][0:num['steps']-1]:
            f.write('%s\n'%(value[0]))

    #l0_exc_population.print_v('%s_exc_0.v' % (file_stem,),compatible_output=False)

    print "[%d] Finishing" % node
    pynn.end()
    print "[%d] Done" % node

