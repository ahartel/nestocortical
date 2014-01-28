import numpy as np
import scipy.io as sio
import sys, socket

from pyNN.utility import get_script_args

simulator_name = 'nest'
try:
    simulator_name = get_script_args(1)[0]
except Exception:
    print "Using default simulator nest"

exec("from pyNN.%s import *" % simulator_name)

from pyNN.random import NumpyRNG

seed = 764756387
tstop = 50.0 # ms
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
num['inputs'] = 1024#*3
num['conns_per_input'] = 5

basepath = '/home/ahartel/data/SVHN/train'

def setupNetwork():
    node = setup(timestep=0.1, min_delay=1.0, max_delay=1.0, debug=True, quit_on_end=False)
    print "Process with rank %d running on %s" % (node, socket.gethostname())


    rng = NumpyRNG(seed=seed, parallel_safe=True)

    #n_spikes = int(2*tstop*input_rate/1000.0)
    #spike_times = numpy.add.accumulate(rng.next(n_spikes, 'exponential',
    #                       [1000.0/input_rate], mask_local=False))

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

    return node,input_populations

if __name__ == "__main__":
    node,input_populations = setupNetwork()

    file_stem = "Results/wta_np%d_%s" % (num_processes(), simulator_name)
    #projection.saveConnections('%s.conn' % file_stem)

    #for file in glob.glob(basepath+'/*.png'):
    #    print "Processing file "+file
    #    f = open(file,'rb')
    #    r = png.Reader(file=f)
    #    image = r.read()
    #    print image
    #    cnt = 0
    #    subcnt=0
    #    for row in image[2]:
    #        cnt+=1
    #        subcnt=0
    #        for pixel in row:
    #           subcnt+=1 
    #    print subcnt/3,cnt

    mat = sio.loadmat(basepath+'/train_32x32.mat')
    data = np.array(mat['X'])
    stop=100
    for i in range(len(mat['y'])):
        if stop==0:
            break
        cnt = 0
        # prepare input population firing rates
        for row in data[:,:,:,i]:
            for pixel in row:
                total=0
                for value in pixel:
                    total+=value
                input_populations[cnt].set('rate',100.0/(3*256)*value)
                cnt+=1

        print "[%d] Running simulation" % node
        run(tstop)
        stop-=1

