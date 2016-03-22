import sys
import nest
import numpy as np
import pickle as pkl
import nest.raster_plot
import nest.voltage_trace

nest.Install("mymodule")

t_sim = 1000.0  # how long we simulate
n_ex = 16000     # size of the excitatory population
n_in = 4000      # size of the inhibitory population
r_expect = 15.0       # mean rate of the ex5itatory population
r_inp = 20.0      # initial rate of the inhibitory population
r_inp_bg = 60.0
epsc_bg = 15.0      # peak amplitude of excitatory synaptic currents
ipsc_bg = -5.0      # peak amplitude of excitatory synaptic currents
epsc = 40.0
d = 1.0          # synaptic delay

NUM_RUNS = 2000
NUM_NEURONS = 1
PLOT_WEIGHTS = False
NUM_BG_INH = 2
NUM_BG_EXC = 2
NUM_BG = NUM_BG_INH + NUM_BG_EXC

mean_R = 0.5
rewards = []
mean_rewards = []
successes = []
figures = []
weight_diff_storage = np.zeros((NUM_RUNS,(32-NUM_BG)*NUM_NEURONS,1))
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
    reshaped = np.reshape(weights,((32-NUM_BG),NUM_NEURONS))
    f = plt.figure()
    plt.imshow(reshaped,interpolation='none')
    plt.colorbar()
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
    mean_R = mean_R + (reward-mean_R)/5.0
    mean_rewards.append(mean_R)

def set_up_network():
    # The actual neuron population
    neuronpop = nest.Create("iaf_neuron", NUM_NEURONS, params=ndict)
    for neuron in neuronpop:
        nest.SetStatus([neuron], {"tau_m": np.random.uniform(15.0,25.0)})

    # The background noise that will be connected with plastic synapses
    noise = nest.Create("poisson_generator", 32-NUM_BG)
    nest.SetStatus(noise, {"rate": r_inp})
    # They need to be parroted to allow STDP
    inputs = nest.Create("parrot_neuron", 32-NUM_BG)
    nest.Connect(noise,inputs,{'rule':'one_to_one'})

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
        background_inh = nest.Create("poisson_generator",NUM_BG_INH)
        background_exc = nest.Create("poisson_generator",NUM_BG_EXC)
        nest.SetStatus(background_inh, {"rate": r_inp_bg})
        nest.SetStatus(background_exc, {"rate": r_inp_bg})
        nest.Connect(background_exc,neuronpop,conn_dict,bg_syn_dict_exc)
        nest.Connect(background_inh,neuronpop,conn_dict,bg_syn_dict_inh)

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

    pkl.dump(rates,open("data/firing_rates.pkl",'w'))

    pkl.dump(get_weights(inputs),open("data/final_weights.pkl",'w'))
    # f = plot_weights(get_weights(inputs))
    # if SAVEFIG:
        # f.savefig("plots/final_weights.png")

    pkl.dump((rewards, successes, mean_rewards),open('data/rewards.pkl','w'))
    pkl.dump(weight_diff_storage, open('data/weight_diffs.pkl','w'))

