"""RSTDP experiment for Hicann-DLS. Here, it is implemented with Nest."""
# import sys
import nest
import math
import copy
import numpy as np
import pickle as pkl
import nest.raster_plot
import nest.voltage_trace
from spike_train import vp_metric_other

nest.Install("mymodule")

TSIM = 1000.0  # how long we simulate
r_inp = 40.0
r_inp_bg = 100.0
epsc_bg = 15.0
ipsc_bg = -10.0
EPSC = 20.0

# COST = 10.0
COST = 0.20

NUM_RUNS = 2000
NUM_NEURONS = 3
PLOT_WEIGHTS = False
NUM_BG_INH = 1
NUM_BG_EXC = 1
NUM_BG = NUM_BG_INH + NUM_BG_EXC

figures = []
weight_diff_storage = np.zeros((NUM_RUNS, (32-NUM_BG)*NUM_NEURONS, 1))
rates = np.zeros((NUM_NEURONS, NUM_RUNS))

NEURON_DICT = {
    "tau_m": 20.0,
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

# def plot_weights(weights):
    # reshaped = np.reshape(weights,((32-NUM_BG),NUM_NEURONS))
    # f = plt.figure()
    # plt.imshow(reshaped,interpolation='none')
    # plt.colorbar()
    # return f

def get_spiketrains(spikedetector):
    events = nest.GetStatus(spikedetector, ["events"])[0][0]
    out = [[] for nrn in range(NUM_NEURONS)]
    for nrn, time in zip(events['senders'], events['times']):
        out[nrn-1].append(time)

    return out

def calculate_reward(run, spikedetector, target):
    global rates
    reward = 0.0

    out = get_spiketrains(spikedetector)

    for neuron in range(NUM_NEURONS):
        num = len(out[neuron])
        print "Measured:",out[neuron]
        print " ",num
        print "Target:",target[neuron]
        print " ",len(target[neuron])

        total_spikes = num + len(target[neuron])
        distance = vp_metric_other(target[neuron], out[neuron], COST)
        print "Distance:",distance

        add_reward = 1.0 - distance/total_spikes
        print "Reward:",add_reward
        reward += add_reward

        rates[neuron][run] = num

    reward /= float(NUM_NEURONS)

    return reward, out

def apply_reward(pop, weights_before, weights_after, reward, mean_reward):
    """Set the new weights of pop using set_weights. The weights are calculated
    as::
        new_weights = (weights_after-weights_before)*success + weights_before
    """

    success = reward-mean_reward

    new_weights = (weights_after-weights_before)*success*10.0 + weights_before

    set_weights(pop, new_weights)

    return success


def set_up_network(epsc):
    """Configure neuron populations.
    ========== ================= =================
    name       number of neurons type
    ========== ================= =================
    neuronpop  NUM_NEURONS       iaf_neuron
    noise      32-NUM_BG         poisson_generator
    inputs     32-NUM_BG         parrot_neuron
    background NUM_BG            poisson_generator
    ========== ================= =================
    """
    # The actual neuron population
    neuronpop = nest.Create("iaf_neuron", NUM_NEURONS, params=NEURON_DICT)
    for neuron in neuronpop:
        nest.SetStatus([neuron], {"tau_m": np.random.uniform(15.0, 25.0)})

    # The background noise that will be connected with plastic synapses
    noise = nest.Create("poisson_generator", 32-NUM_BG)
    nest.SetStatus(noise, {"rate": r_inp})
    # They need to be parroted to allow STDP
    inputs = nest.Create("parrot_neuron", 32-NUM_BG)
    nest.Connect(noise, inputs, {'rule':'one_to_one'})

    # Connect the parrots to the neurons under test
    conn_dict = {"rule": "all_to_all"}
    syn_dict = {"model": "rstdp_synapse",
                "mu_plus":0.0,
                "mu_minus":0.0,
                "alpha": 1.0,
                "lambda": 0.0001,
                "weight": epsc}
    nest.Connect(inputs, neuronpop, conn_dict, syn_dict)

    # Apply some non-changing background
    if NUM_BG > 0:
        bg_syn_dict_exc = {"model": "static_synapse",
                           "weight": epsc_bg}
        bg_syn_dict_inh = {"model": "static_synapse",
                           "weight": ipsc_bg}
        background_inh = nest.Create("poisson_generator", NUM_BG_INH)
        background_exc = nest.Create("poisson_generator", NUM_BG_EXC)
        nest.SetStatus(background_inh, {"rate": r_inp_bg})
        nest.SetStatus(background_exc, {"rate": r_inp_bg})
        nest.Connect(background_exc, neuronpop, conn_dict, bg_syn_dict_exc)
        nest.Connect(background_inh, neuronpop, conn_dict, bg_syn_dict_inh)

    voltmeter = nest.Create("voltmeter", NUM_NEURONS)
    spikedetector = nest.Create("spike_detector")

    nest.SetStatus(voltmeter, {"withgid": True, "withtime": True})

    nest.Connect(neuronpop, spikedetector)#, {'rule':'one_to_one'})
    nest.Connect(voltmeter, neuronpop)

    return inputs, neuronpop, voltmeter, spikedetector

def generate_target_spiketrain(pop, spikedetector, epsc):
    old_weights = get_weights(pop)
    weights = copy.copy(old_weights)
    for row in range(len(weights)):
        weights[row] = 5*math.sin(float(row)/10.0) + epsc
    print weights
    set_weights(pop, weights)
    nest.Simulate(TSIM)
    target_trains = get_spiketrains(spikedetector)
    print target_trains

    return target_trains

if __name__ == '__main__':
    rewards = []
    mean_R = 0.5
    successes = []
    mean_rewards = []
    spiketrains = []

    inputs, neuronpop, voltmeter, spikedetector = set_up_network(EPSC)

    target = [[] for nrn in range(NUM_NEURONS)]
    is_empty = lambda x : not x
    while any(map(is_empty, target)):
        target = generate_target_spiketrain(inputs, spikedetector, EPSC)

    nest.ResetKernel()
    inputs, neuronpop, voltmeter, spikedetector = set_up_network(EPSC)

    for run in range(NUM_RUNS):
        run_str = "%03d" % (run,)
        print "Run:", run_str

        weights_before = get_weights(inputs)
        # print weights_before

        # if PLOT_WEIGHTS:
            # f = plot_weights(weights_before)
            # if SAVEFIG:
                # f.savefig('plots/'+run_str+'_before_weights.png')

        nest.Simulate(TSIM)

        # lines = nest.voltage_trace.from_device([voltmeter[1]])
        # lines[0][0].figure.savefig('plots/'+run_str+'_voltage_trace.png')
        # f = nest.raster_plot.from_device(spikedetector, hist=True)
        # f[0].figure.savefig('plots/'+run_str+'_raster_plot.png')

        reward, spiketrains_run = calculate_reward(run, spikedetector, target)
        spiketrains.append(spiketrains_run)

        weights_after = get_weights(inputs)
        weight_diff_storage[run] = weights_after-weights_before

        nest.ResetKernel()
        inputs, neuronpop, voltmeter, spikedetector = set_up_network(EPSC)

        success = apply_reward(inputs, weights_before, weights_after, reward,
                               mean_R)

        rewards.append(reward)
        successes.append(success)
        mean_R = mean_R + (reward-mean_R)/5.0
        mean_rewards.append(mean_R)

        # if PLOT_WEIGHTS:
            # f = plot_weights((weights_after-weights_before)*reward)
            # if SAVEFIG:
                # f.savefig('plots/'+run_str+'_weight_diff.png')
            # plt.figure()

    pkl.dump(rates, open("data/firing_rates.pkl", 'w'))
    pkl.dump(spiketrains, open("data/spiketrains.pkl", 'w'))
    pkl.dump(target, open("data/target_spiketrains.pkl", 'w'))

    pkl.dump(get_weights(inputs), open("data/final_weights.pkl", 'w'))
    # f = plot_weights(get_weights(inputs))
    # if SAVEFIG:
        # f.savefig("plots/final_weights.png")

    pkl.dump((rewards, successes, mean_rewards), open('data/rewards.pkl', 'w'))
    pkl.dump(weight_diff_storage, open('data/weight_diffs.pkl', 'w'))

