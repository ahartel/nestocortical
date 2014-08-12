import numpy as np
import scipy.io as sio
import sys, socket, png, pickle
from collections import deque

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
num['l0_exc_neurons'] = 64
num['l0_exc_maxneighbors'] = 4
num['l1_exc_neurons'] = 16
num['l1_exc_maxneighbors'] = 4
num['l0_l1_maxneighbors'] = 4
num['l0_inh_neurons'] = 20
num['l1_inh_neurons'] = 5
num['inputs'] = 1024*3
num['inputs_maxneighbors'] = 4
num['steps'] = 50
num['steps_firing_rate_average'] = 10

assert(num['inputs']%num['l0_exc_neurons']==0)
assert(num['l0_exc_neurons']%num['l1_exc_neurons']==0)

# input -> exc0
w_inp_exc0_peak = 0.0015
sigma_inp_exc0 = 5.
w_inp_exc0_max = 0.005

# exc0 -> exc1
sigma_exc0_exc1 = 4.
w_exc0_exc1_peak = 0.005
w_exc0_exc1_max = 0.005

# exc0 -> inh0
p_exc0_inh0 = 0.6
w_exc0_inh0 = 0.01

# exc0 -> exc0
sigma_exc0_exc0 = 7.
w_exc0_exc0_max = 0.001

# exc1 -> exc1
sigma_exc1_exc1 = 7.
w_exc1_exc1_max = 0.001

# exc1 -> inh1
p_exc1_inh1 = 1.0
w_exc1_inh1 = 0.02

# inh0 -> exc0
p_inh0_exc0 = 0.6
w_inh0_exc0 = 0.01

# inh1 -> exc1
p_inh1_exc1 = 1.0
w_inh1_exc1 = 0.1

basepath = '/home/ahartel/data/SVHN/train'

def connect_gauss(num_pre,num_post,sigma,w_max,max_neighbors,weights,avoid_self_conn):
    # stimulus
    for i in range(num_post):
        for d in range(-max_neighbors, max_neighbors,  + 1):
            for n in range(num_pre/num_post*(i+d),num_pre/num_post*(i+d+1)):
                k = n%num_pre
                w = w_max
                if sigma > 0.:
                    w *= np.exp(-(d**2)/(sigma**2))

                #if np.random.random() < p_connect:
                #    print w
                #pynn.connect(input_population.cell[k], l0_exc_population.cell[i], weight=w, synapse_type='excitatory')
                #pynn.Projection(stim, ne[k], method=pynn.AllToAllConnector(weights=w), tar    get='excitatory')
                if not (avoid_self_conn and i==k):
                    weights[k*num_post+i] = w

    return weights


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
    exc_connector = pynn.AllToAllConnector(weights=0.0)
    l0_exc_exc_projection = pynn.Projection(l0_exc_population,l0_exc_population,exc_connector)
    exc0_exc0_weights = l0_exc_exc_projection.getWeights()

    exc0_exc0_weights = connect_gauss(num['l0_exc_neurons'],num['l0_exc_neurons'],sigma_exc0_exc0,w_exc0_exc0_max,num['l0_exc_maxneighbors'],exc0_exc0_weights,True)

    l0_exc_exc_projection.setWeights(exc0_exc0_weights)

    # 6) exc1 -> exc1
    exc_connector = pynn.AllToAllConnector(weights=0.0)
    l1_exc_exc_projection = pynn.Projection(l1_exc_population,l1_exc_population,exc_connector)
    exc1_exc1_weights = l1_exc_exc_projection.getWeights()

    exc1_exc1_weights = connect_gauss(num['l1_exc_neurons'],num['l1_exc_neurons'],sigma_exc1_exc1,w_exc1_exc1_max,num['l1_exc_maxneighbors'],exc1_exc1_weights,True)

    l1_exc_exc_projection.setWeights(exc1_exc1_weights)


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
        A_plus=0.012, A_minus=0.012)
    )

    connector = pynn.AllToAllConnector(weights=0.0)
    input_projection = pynn.Projection(
            input_population,
            l0_exc_population,
            connector,
            rng=rng,
            synapse_dynamics=pynn.SynapseDynamics(slow=stdp_model)
        )

    input_weights = input_projection.getWeights()

    print "[%d] Creating input projections" % node
    input_weights = connect_gauss(num['inputs'],num['l0_exc_neurons'],sigma_inp_exc0,w_inp_exc0_peak,num['inputs_maxneighbors'],input_weights,False)

    input_projection.setWeights(input_weights)

    # 11) exc0 -> exc1
    stdp_model = pynn.STDPMechanism(
        timing_dependence=pynn.SpikePairRule(tau_plus=20.0, tau_minus=20.0),
        weight_dependence=pynn.AdditiveWeightDependence(w_min=0, w_max=w_exc0_exc1_max,
        A_plus=0.012, A_minus=0.012)
    )

    connector = pynn.AllToAllConnector(weights=0.0)
    l1_projection = pynn.Projection(
            l0_exc_population,
            l1_exc_population,
            connector,
            rng=rng,
            synapse_dynamics=pynn.SynapseDynamics(slow=stdp_model)
        )

    exc0_exc1_weights = l1_projection.getWeights()

    print "[%d] Creating input projections" % node
    exc0_exc1_weights = connect_gauss(num['l0_exc_neurons'],num['l1_exc_neurons'],sigma_exc0_exc1,w_exc0_exc1_peak,num['l0_l1_maxneighbors'],exc0_exc1_weights,False)

    l1_projection.setWeights(exc0_exc1_weights)


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

    # average firing rates
    mean_l0 = deque()
    mean_l1 = deque()

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

        mean_l0.appendleft(l0_exc_population.meanSpikeCount())
        mean_l1.appendleft(l1_exc_population.meanSpikeCount())

        if num['steps']-stop > num['steps_firing_rate_average']:
            mean0_array = np.array(mean_l0)
            mean1_array = np.array(mean_l1)
            avg_mean_l0 = np.mean(mean0_array[0:num['steps_firing_rate_average']-1]-mean0_array[1:-1])/float(tstop)/1e-3
            avg_mean_l1 = np.mean(mean1_array[0:num['steps_firing_rate_average']-1]-mean1_array[1:-1])/float(tstop)/1e-3
            print avg_mean_l0,avg_mean_l1

            new_A_minus_l0 = (avg_mean_l0*avg_mean_l0-1600.0)/800.0/10.0+1.1
            new_A_minus_l1 = (avg_mean_l1*avg_mean_l1-225.0)/122.5/10.0+1.1
            print new_A_minus_l0,new_A_minus_l1

            input_projection.setSynapseDynamics('A_minus', new_A_minus_l0)
            l1_projection.setSynapseDynamics('A_minus', new_A_minus_l1)

            mean_l0.pop()
            mean_l1.pop()

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

