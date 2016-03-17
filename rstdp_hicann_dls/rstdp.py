import sys
SAVEFIG=True
if SAVEFIG:
    import matplotlib as mpl
    mpl.use('Agg')
import nest
import nest.voltage_trace
import nest.raster_plot
import numpy as np
import matplotlib.pyplot as plt

nest.Install("mymodule")

t_sim = 1000.0  # how long we simulate
n_ex = 16000     # size of the excitatory population
n_in = 4000      # size of the inhibitory population
r_expect = 35.0       # mean rate of the ex5itatory population
r_inp = 40.0      # initial rate of the inhibitory population
epsc = 10.0      # peak amplitude of excitatory synaptic currents
ipsc = -45.0     # peak amplitude of inhibitory synaptic currents
d = 1.0          # synaptic delay
lower = 15.0     # lower bound of the search interval
upper = 25.0     # upper bound of the search interval
prec = 0.01      # how close need the excitatory rates be

NUM_RUNS = 2000
NUM_NEURONS = 5
PLOT_WEIGHTS = False

mean_R = 0.5
rewards = []
mean_rewards = []
successes = []
figures = []
# sum_of_weight_updates = np.array([[0.0] for i in range(32*5)])
weight_diff_storage = np.zeros((NUM_RUNS,32*5,1))
rates = np.zeros((NUM_NEURONS,NUM_RUNS))

ndict = {
            "tau_m": 20.0,
        }

def get_weights(pop):
    conns = nest.GetConnections(pop, synapse_model="rstdp_synapse")
    conn_vals = nest.GetStatus(conns, ["accumulation"])
    conn_vals = np.array(conn_vals)
    return conn_vals

def set_weights(pop,weights):
    conns = nest.GetConnections(pop, synapse_model="rstdp_synapse")
    for conn,wgt in zip(conns,weights):
        nest.SetStatus([conn], {"weight": wgt[0]} )
    # check if it worked
    # plot_weights(np.array(nest.GetStatus(conns, ["weight"])))

def plot_weights(weights):
    reshaped = np.reshape(weights,(32,5))
    f = plt.figure()
    plt.imshow(reshaped,interpolation='none')
    plt.colorbar()
    return f

def movingaverage (values, window):
    weights = np.repeat(1.0, window)/window
    sma = np.convolve(values, weights, 'valid')
    return sma

def plot_rates():
    global rates
    f = plt.figure()
    for nrn in range(NUM_NEURONS):
        av = movingaverage(rates[nrn],5)
        ax = plt.plot(np.arange(NUM_RUNS),rates[nrn],'x')
        plt.plot(np.arange(NUM_RUNS)[NUM_RUNS-len(av):],av,'-',
                 color = ax[0].get_color())
    return f

def plot_rewards():
    global rewards
    global successes
    global mean_rewards

    f,axr = plt.subplots(1)
    axr.plot(rewards,'-b')
    axr.plot(mean_rewards,'--b')
    axr.set_xlabel("Run number")
    axr.set_ylabel("Reward")

    axl = axr.twinx()
    axl.plot(successes,'xr')
    # axl.axhline(np.mean(successes),linestyle='--',color='r')
    av = movingaverage(successes,50)
    axl.plot(np.arange(NUM_RUNS)[NUM_RUNS-len(av):], av,'-r')
    axl.set_ylabel("Success")
    return f

def calculate_reward(run,spikedetector):
    global rates
    R = 0.0
    events = nest.GetStatus(spikedetector,["events"])[0][0]
    out = [[] for nrn in range(NUM_NEURONS)]
    for nrn,time in zip(events['senders'],events['times']):
        out[nrn-1].append(time)

    for neuron in range(NUM_NEURONS):
        # out = nest.GetStatus(spikedetector, "n_events")[0]
        # out *= 1000.0 / t_sim
        num = len(out[neuron])
        # print("  -> Neuron %d rate: %6.2f Hz (goal: %4.2f Hz)" \
                # % (neuron, num, r_expect))

        R += 1.0 - float(abs(num-r_expect)) / float(num+r_expect)
        rates[neuron][run] = num

    R /= float(NUM_NEURONS)

    return R

def apply_reward(pop,weights_before,weights_after,reward):
    global mean_R
    success = reward-mean_R

    new_weights = (weights_after-weights_before)*reward + weights_before

    set_weights(pop,new_weights)

    rewards.append(reward)
    successes.append(success)
    mean_R = reward + (reward-mean_R)/5.0
    mean_rewards.append(mean_R)

def set_up_network():
    # The actual neuron population
    neuronpop = nest.Create("iaf_neuron", NUM_NEURONS, params=ndict)
    for neuron in neuronpop:
        nest.SetStatus([neuron], {"tau_m": np.random.uniform(15.0,25.0)})

    # The background noise that will be connected with plastic synapses
    noise = nest.Create("poisson_generator", 32)
    nest.SetStatus(noise, {"rate": r_inp})
    # They need to be parroted to allow STDP
    inputs = nest.Create("parrot_neuron",32)
    nest.Connect(noise,inputs,{'rule':'one_to_one'})

    # Connect the parrots to the neurons under test
    conn_dict = {"rule": "all_to_all"}
    syn_dict = {"model": "rstdp_synapse",
                "mu_plus":0.0,
                "mu_minus":0.0,
                "alpha": 1.0,
                "lambda": 0.0005,
                "weight": epsc}
    nest.Connect(inputs, neuronpop, conn_dict, syn_dict)

    # Apply some non-changing background
    bg_syn_dict = {"model": "static_synapse",
                   "weight": 2*epsc}
    background = nest.Create("poisson_generator",1)
    nest.SetStatus(background, {"rate": 15*r_inp})
    nest.Connect(background,neuronpop,conn_dict,bg_syn_dict)

    voltmeter = nest.Create("voltmeter",NUM_NEURONS)
    spikedetector = nest.Create("spike_detector")

    nest.SetStatus(voltmeter, {"withgid": True, "withtime": True})

    nest.Connect(neuronpop, spikedetector)#, {'rule':'one_to_one'})
    nest.Connect(voltmeter, neuronpop)

    return inputs,neuronpop,voltmeter,spikedetector

if __name__ == '__main__':

    inputs, neuronpop, voltmeter, spikedetector = set_up_network()

    for run in range(NUM_RUNS):
        run_str = "%03d" % (run,)
        print "Run:",run_str

        weights_before = get_weights(inputs)
        # print weights_before

        if PLOT_WEIGHTS:
            f = plot_weights(weights_before)
            if SAVEFIG:
                f.savefig('plots/'+run_str+'_before_weights.png')

        nest.Simulate(t_sim)

        # lines = nest.voltage_trace.from_device([voltmeter[1]])
        # lines[0][0].figure.savefig('plots/'+run_str+'_voltage_trace.png')
        # f = nest.raster_plot.from_device(spikedetector, hist=True)
        # f[0].figure.savefig('plots/'+run_str+'_raster_plot.png')

        reward = calculate_reward(run,spikedetector)

        weights_after = get_weights(inputs)
        weight_diff_storage[run] = weights_after-weights_before

        nest.ResetKernel()
        inputs, neuronpop, voltmeter, spikedetector = set_up_network()

        apply_reward(inputs,weights_before,weights_after,reward)

        if PLOT_WEIGHTS:
            f = plot_weights((weights_after-weights_before)*reward)
            if SAVEFIG:
                f.savefig('plots/'+run_str+'_weight_diff.png')
            plt.figure()

    f = plot_rates()
    if SAVEFIG:
        f.savefig("plots/firing_rates.png")

    f = plot_weights(get_weights(inputs))
    if SAVEFIG:
        f.savefig("plots/final_weights.png")

    f = plot_rewards()
    if SAVEFIG:
        f.savefig("plots/rewards.png")

    if not SAVEFIG:
        plt.show()

    # Data evaluation
    mean_success = np.mean(successes)
    print "Mean success:", mean_success
    success_from_mean = successes - mean_success

    mean_eij = np.mean(weight_diff_storage,0)
    # print "Mean eligibility * mean success:", mean_eij * mean_success

    cov = 0
    for run in range(NUM_RUNS):
        cov += (successes[run] - mean_success) \
                * (weight_diff_storage[run] - mean_eij)
    cov /= float(NUM_RUNS)

    print np.reshape(cov,(32,5))
    print np.reshape(mean_eij,(32,5))

    f,ax = plt.subplots(1,2)
    ax[0].imshow(np.reshape(cov,(32,5)),
                 interpolation='none')
    ax[0].set_title("Covariance")
    ax[1].imshow(np.reshape(mean_eij * mean_success,(32,5)),
                 vmin=np.min(cov),
                 vmax=np.max(cov),
                 interpolation='none')
    ax[1].set_title("Mean eij")
    PCM=ax[1].get_children()[2]
    plt.colorbar(PCM, ax=ax[1])
    f.savefig("plots/mean_delta_w.png")


