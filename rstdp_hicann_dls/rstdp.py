"""RSTDP experiment for Hicann-DLS. Here, it is implemented with Nest."""
# import sys
import numpy as np
import nest
import math
import copy
import random
import pickle as pkl
import nest.raster_plot
import nest.voltage_trace
import matplotlib.pyplot as plt
from spike_train import vp_metric_other

nest.Install("mymodule")

SEED = 42

TSIM = 1000.0  # how long we simulate
R_INP = 8.0
R_INP_BG = 0.1
EPSC_BG = 100.0
IPSC_BG = -5.0
EPSC = 14.0
TARGET_EPSP = 30.0

# COST = 10.0
COST = 0.10

NUM_RUNS = 5000
NUM_NEURONS = 1
NUM_BG_INH = 1
NUM_BG_EXC = 20
NUM_BG = NUM_BG_INH + NUM_BG_EXC


NEURON_DICT = {
    "tau_m": 30.0,
    "V_th": -68.0
    }

SYN_DICT = {"model": "rstdp_synapse",
            "mu_plus":0.0,
            "mu_minus":0.0,
            "alpha": 1.0,
            # "lambda": 0.0001,
            "lambda": 0.004,
            "tau_plus": 20.0,
            "Wmax": 200.0,
            # "tau_minus": 20.0,
            # "weight": {'distribution': 'normal_clipped', 'low': 0.5,
            #            'mu': EPSC/1.0, 'sigma': EPSC/4.0}}
            # "weight": {'distribution': 'uniform', 'low': EPSC*0.7,
            #            'high': EPSC*1.3}}
            'weight': EPSC}


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


def get_spiketrains(nrnpop, spikedetector):
    events = nest.GetStatus(spikedetector, ["events"])[0][0]
    out = [[] for nrn in range(NUM_NEURONS)]
    for nrn, time in zip(events['senders'], events['times']):
        out[nrnpop.index(nrn)].append(time)

    return out

def calculate_reward(nrnpop, spikedetector, target):
    reward = 0.0
    rates = np.zeros(NUM_NEURONS)

    out = get_spiketrains(nrnpop, spikedetector)

    for neuron in range(NUM_NEURONS):
        num = len(out[neuron])
        # print "Measured:", out[neuron]
        # print " ", num
        # print "Target:", target[neuron]
        # print " ", len(target[neuron])

        total_spikes = num + len(target[neuron])
        distance = vp_metric_other(target[neuron], out[neuron], COST)
        print "Distance:", distance

        add_reward = 1.0 - distance/total_spikes
        print "Reward:", add_reward
        reward += add_reward

        rates[neuron] = num

    reward /= float(NUM_NEURONS)

    return reward, out, rates

def apply_reward(pop, wgt_before, wgt_after, reward, mean_reward):
    """Set the new weights of pop using set_weights. The weights are calculated
    as::
        new_weights = (wgt_after-wgt_before)*success + wgt_before
    """

    success_signal = reward-mean_reward

    new_weights = (wgt_after-wgt_before)*success_signal*1.0 + wgt_before

    set_weights(pop, new_weights)

    return success_signal


def set_up_network_poisson_input():
    """Configure neuron populations.
    ========== ================= =================
    name       number of neurons type
    ========== ================= =================
    noise      32-NUM_BG         poisson_generator
    inputs     32-NUM_BG         parrot_neuron
    ========== ================= =================
    """
    # The actual random input that will be connected with plastic synapses
    noise = nest.Create("poisson_generator", 32-NUM_BG)
    nest.SetStatus(noise, {"rate": R_INP})
    # They need to be parroted to allow STDP
    inputs = nest.Create("parrot_neuron", 32-NUM_BG)
    nest.Connect(noise, inputs, {'rule':'one_to_one'})

    return set_up_network_trunk(inputs)

def set_up_network_serial_input():
    """Configure neuron populations.
    ========== ================= =================
    name       number of neurons type
    ========== ================= =================
    inputs     32-NUM_BG         spike_generator
    ========== ================= =================
    """
    source = nest.Create('spike_generator', 32-NUM_BG)
    for inpt in range(32-NUM_BG):
        nest.SetStatus([source[inpt]],
                       {'spike_times':[1.0 + 30.0 * float(inpt),]})
                                       # 2.0 + 30.0 * float(inpt),
                                       # 3.0 + 30.0 * float(inpt),
                                       # 4.0 + 30.0 * float(inpt),
                                       # 5.0 + 30.0 * float(inpt)]})

    # They need to be parroted to allow STDP
    inputs = nest.Create("parrot_neuron", 32-NUM_BG)
    nest.Connect(source, inputs, {'rule':'one_to_one'})

    return set_up_network_trunk(inputs)

def set_up_network_trunk(inputs):
    """Configure neuron populations.
    ========== ================= =================
    name       number of neurons type
    ========== ================= =================
    neuronpop  NUM_NEURONS       iaf_neuron
    background NUM_BG            poisson_generator
    ========== ================= =================
    """

    # The actual neuron population
    neuronpop = nest.Create("iaf_neuron", NUM_NEURONS, params=NEURON_DICT)
    for neuron in neuronpop:
        # print nest.GetStatus([neuron])
        nest.SetStatus([neuron], {"tau_m": np.random.uniform(25.0, 35.0)})

    # Connect the parrots to the neurons under test
    conn_dict = {"rule": "all_to_all"}
    nest.Connect(inputs, neuronpop, conn_dict, SYN_DICT)

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

def generate_target_spiketrain(inputpop, nrnpop, spikedetector):
    """Apply a fixed weight pattern to the input population and simulate for
    TSIM to get a target output spike train."""
    old_weights = get_weights(inputpop)
    weights = copy.copy(old_weights)
    for row in range(len(weights)):
        weights[row] = TARGET_EPSP*math.sin(float(row)/5.0)
        # weights[row] = random.randint(0, 1) * TARGET_EPSP
        # weights[row] = 0
    # weights[int((32-NUM_BG)/2)] = TARGET_EPSP
    print weights
    set_weights(inputpop, weights)
    nest.Simulate(TSIM)
    target_trains = get_spiketrains(nrnpop, spikedetector)
    print target_trains

    return target_trains

def reset_kernel():
    old_seed = nest.GetStatus([0])[0]['rng_seeds'][0]
    nest.ResetKernel()
    nest.SetStatus([0], {'rng_seeds': (old_seed + 1,)})
    # print old_seed,nest.GetStatus([0])


def main_function():
    """This function exists only to tell pylint that the following variables
    are variables and not functions."""
    rewards = []
    mean_reward = 0.5
    successes = []
    mean_rewards = []
    spiketrains = []
    weight_diff_storage = np.zeros((NUM_RUNS, (32-NUM_BG)*NUM_NEURONS, 1))
    rates = np.zeros((NUM_RUNS, NUM_NEURONS))

    target = [[] for nrn in range(NUM_NEURONS)]
    is_empty = lambda x: not x
    while any([is_empty(tgt) for tgt in target]):
        reset_kernel()
        # inputs, neuronpop, voltmeter, spikedetector = \
                                                # set_up_network_serial_input()
        inputs, neuronpop, voltmeter, spikedetector = \
                                                set_up_network_poisson_input()
        target = generate_target_spiketrain(inputs, neuronpop, spikedetector)
        nest.voltage_trace.from_device([voltmeter[0]])
        plt.show()

    target_weights = get_weights(inputs)

    reset_kernel()
    # inputs, neuronpop, voltmeter, spikedetector = set_up_network_serial_input()
    inputs, neuronpop, voltmeter, spikedetector = set_up_network_poisson_input()

    initial_weights = get_weights(inputs)

    for run in range(NUM_RUNS):
        run_str = "%03d" % (run,)
        print "Run:", run_str

        weights_before = get_weights(inputs)
        # print weights_before

        nest.Simulate(TSIM)

        # lines = nest.voltage_trace.from_device([voltmeter[0]])
        # lines[0][0].figure.savefig('plots/'+run_str+'_voltage_trace.png')
        # plt.show()
        # f = nest.raster_plot.from_device(spikedetector, hist=True)
        # f[0].figure.savefig('plots/'+run_str+'_raster_plot.png')

        reward, spiketrains_run, rates[run] = calculate_reward(neuronpop,
                                                               spikedetector,
                                                               target)
        spiketrains.append(spiketrains_run)

        weights_after = get_weights(inputs)
        weight_diff_storage[run] = weights_after-weights_before

        reset_kernel()
        # inputs, neuronpop, voltmeter, spikedetector = set_up_network_serial_input()
        inputs, neuronpop, voltmeter, spikedetector = \
                                                set_up_network_poisson_input()

        success = apply_reward(inputs, weights_before, weights_after, reward,
                               mean_reward)

        rewards.append(reward)
        successes.append(success)
        mean_reward = mean_reward + (reward-mean_reward)/5.0
        mean_rewards.append(mean_reward)

    pkl.dump(rates, open("data/firing_rates.pkl", 'w'))
    pkl.dump(spiketrains, open("data/spiketrains.pkl", 'w'))
    pkl.dump(target, open("data/target_spiketrains.pkl", 'w'))

    pkl.dump(target_weights, open("data/target_weights.pkl", 'w'))
    pkl.dump(initial_weights, open("data/initial_weights.pkl", 'w'))
    pkl.dump(get_weights(inputs), open("data/final_weights.pkl", 'w'))

    pkl.dump((rewards, successes, mean_rewards), open('data/rewards.pkl', 'w'))
    pkl.dump(weight_diff_storage, open('data/weight_diffs.pkl', 'w'))

if __name__ == '__main__':
    random.seed(1)
    np.random.seed(seed=1)
    nest.SetStatus([0], {'rng_seeds': (SEED,)})
    print nest.GetStatus([0])
    main_function()

