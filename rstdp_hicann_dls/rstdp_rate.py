"""This experiment implements a R-STDP-based firing rate learning task"""
# import sys
import nest
import numpy as np
import pickle as pkl
import nest.raster_plot
import nest.voltage_trace
import matplotlib.pyplot as plt

nest.Install("mymodule")

T_SIM = 1000.0  # how long we simulate
R_EXPECT = 80.0       # mean rate of the excitatory population
R_INP = 500.0
R_INP_BG = 500.0
EPSC_BG = 50.0      # peak amplitude of excitatory synaptic currents
IPSC_BG = -50.0      # peak amplitude of excitatory synaptic currents
EPSC = 80.0

NUM_RUNS = 1000
NUM_NEURONS = 1
PLOT_WEIGHTS = False
NUM_BG_INH = 8
NUM_BG_EXC = 8
NUM_BG = NUM_BG_INH + NUM_BG_EXC
NUM_INPUTS = 1

NDICT = {
    "tau_m": 10.0,
    "t_ref": 10.0,
    "V_reset": -60.0,
    "E_L": -80.0,
}


def get_weights(pop):
    """Return the weights of all synapes of type rstdp_synapse that connect
    from population pop"""
    conns = nest.GetConnections(pop, synapse_model="rstdp_synapse")
    conn_vals = nest.GetStatus(conns, ["accumulation"])
    conn_vals = np.array(conn_vals)
    return conn_vals

def set_weights(pop, weights):
    """Set weights of synpases of type rstdp_synapse that project from
    population pop."""
    conns = nest.GetConnections(pop, synapse_model="rstdp_synapse")
    for conn, wgt in zip(conns, weights):
        nest.SetStatus([conn], {"weight": wgt[0]})
    # check if it worked
    # plot_weights(np.array(nest.GetStatus(conns, ["weight"])))

def plot_weights(weights):
    """Plot the weights given as argument using imshow. Before plotting, a
    reshape to (NUM_INPUTS ,NUM_NEURONS) takes place."""
    reshaped = np.reshape(weights, (NUM_INPUTS, NUM_NEURONS))
    fig = plt.figure()
    plt.imshow(reshaped, interpolation='none')
    plt.colorbar()
    return fig

def calculate_reward(run_num, spikedetector, firing_rates):
    """Calculate the average reward over all neurons for this run. The reward
    of an individual neuron is calculated using a normalized version of the
    Victor Purpura metric for q=0, i.e. only the rates are  compared."""
    average_reward = 0.0
    events = nest.GetStatus(spikedetector, ["events"])[0][0]
    out = [[] for nrn in range(NUM_NEURONS)]
    for nrn, time in zip(events['senders'], events['times']):
        out[nrn-1].append(time)

    for neuron in range(NUM_NEURONS):
        # out = nest.GetStatus(spikedetector, "n_events")[0]
        # out *= 1000.0 / t_sim
        num = len(out[neuron])
        # print("  -> Neuron %d rate: %6.2f Hz (goal: %4.2f Hz)" \
                # % (neuron, num, R_EXPECT))

        average_reward += 1.0 - float(abs(num-R_EXPECT)) / float(num+R_EXPECT)
        firing_rates[neuron][run_num] = num

    average_reward /= float(NUM_NEURONS)

    return average_reward

def apply_reward(pop, weights_before, weights_after, reward, mean_reward):
    """Set the new weights of pop using set_weights. The weights are calculated
    as
        new_weights = (weights_after-weights_before)*success + weights_before
    """

    success = reward-mean_reward

    # to do RSTDP
    new_weights = (weights_after-weights_before)*success*3.0 + weights_before
    # to measure activation function
    # new_weights = weights_before+0.5

    set_weights(pop, new_weights)

    return success

def set_up_network(epsc):
    # The actual neuron population
    neuronpop = nest.Create("iaf_neuron", NUM_NEURONS, params=NDICT)
    for neuron in neuronpop:
        nest.SetStatus([neuron], {"tau_m": np.random.uniform(15.0, 25.0)})

    # The background noise that will be connected with plastic synapses
    noise = nest.Create("poisson_generator", NUM_INPUTS)
    nest.SetStatus(noise, {"rate": R_INP})
    # They need to be parroted to allow STDP
    inputs = nest.Create("parrot_neuron", NUM_INPUTS)
    nest.Connect(noise, inputs, {'rule':'one_to_one'})

    # Connect the parrots to the neurons under test
    conn_dict = {"rule": "all_to_all"}
    syn_dict = {"model": "rstdp_synapse",
                "mu_plus":0.0,
                "mu_minus":0.0,
                "alpha": 1.0,
                "lambda": 0.0002,
                "weight": epsc,
                "Wmax": 5000.0}
    nest.Connect(inputs, neuronpop, conn_dict, syn_dict)

    # Apply some non-changing background
    if NUM_BG > 0:
        bg_syn_dict_exc = {"model": "static_synapse",
                           "weight": EPSC_BG}
        bg_syn_dict_inh = {"model": "static_synapse",
                           "weight": IPSC_BG}
        background_inh = nest.Create("poisson_generator", NUM_BG_INH)
        background_exc = nest.Create("poisson_generator", NUM_BG_EXC)
        nest.SetStatus(background_inh, {"rate": R_INP_BG})
        nest.SetStatus(background_exc, {"rate": R_INP_BG})
        nest.Connect(background_exc, neuronpop, conn_dict, bg_syn_dict_exc)
        nest.Connect(background_inh, neuronpop, conn_dict, bg_syn_dict_inh)

    voltmeter = nest.Create("voltmeter", NUM_NEURONS)
    spikedetector = nest.Create("spike_detector")

    nest.SetStatus(voltmeter, {"withgid": True, "withtime": True})

    nest.Connect(neuronpop, spikedetector)#, {'rule':'one_to_one'})
    nest.Connect(voltmeter, neuronpop)

    return inputs, neuronpop, voltmeter, spikedetector

if __name__ == '__main__':
    SAVEFIG = False
    mean_R = 0.5
    rewards = []
    mean_rewards = []
    successes = []
    figures = []
    weight_diff_storage = np.zeros((NUM_RUNS, NUM_INPUTS*NUM_NEURONS, 1))
    rates = np.zeros((NUM_NEURONS, NUM_RUNS))

    inputs, neuronpop, voltmeter, spikedetector = set_up_network(epsc=EPSC)

    for run in range(NUM_RUNS):
        run_str = "%03d" % (run,)
        print "Run:", run_str

        weights_before = get_weights(inputs)
        # print weights_before

        if PLOT_WEIGHTS:
            f = plot_weights(weights_before)
            if SAVEFIG:
                f.savefig('plots/'+run_str+'_before_weights.png')

        nest.Simulate(T_SIM)

        # lines = nest.voltage_trace.from_device(voltmeter)
        # lines[0][0].figure.savefig('plots/'+run_str+'_voltage_trace.png')
        # plt.clf()
        # f = nest.raster_plot.from_device(spikedetector, hist=True)
        # f[0].figure.savefig('plots/'+run_str+'_raster_plot.png')

        reward = calculate_reward(run, spikedetector, rates)

        weights_after = get_weights(inputs)
        weight_diff_storage[run] = weights_after-weights_before

        nest.ResetKernel()
        inputs, neuronpop, voltmeter, spikedetector = set_up_network(epsc=EPSC)

        success = apply_reward(inputs, weights_before, weights_after, reward,
                               mean_R)

        rewards.append(reward)
        successes.append(success)
        mean_R = mean_R + (reward-mean_R)/5.0
        mean_rewards.append(mean_R)

        if PLOT_WEIGHTS:
            f = plot_weights((weights_after-weights_before)*reward)
            if SAVEFIG:
                f.savefig('plots/'+run_str+'_weight_diff.png')
            plt.figure()

    pkl.dump(rates, open("data/firing_rates.pkl", 'w'))

    pkl.dump(get_weights(inputs), open("data/final_weights.pkl", 'w'))
    # f = plot_weights(get_weights(inputs))
    # if SAVEFIG:
        # f.savefig("plots/final_weights.png")

    pkl.dump((rewards, successes, mean_rewards), open('data/rewards.pkl', 'w'))
    pkl.dump(weight_diff_storage, open('data/weight_diffs.pkl', 'w'))

