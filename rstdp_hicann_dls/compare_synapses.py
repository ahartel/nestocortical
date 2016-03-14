# import matplotlib as mpl
# mpl.use('Agg')
import nest
import nest.voltage_trace
import nest.raster_plot
import numpy as np
import matplotlib.pyplot as plt

nest.Install("mymodule")

t_sim = 2000.0  # how long we simulate
r_inp = 300.0      # initial rate of the inhibitory population
epsc = 40.0      # peak amplitude of excitatory synaptic currents

ndict = {
            "tau_m": 20.0,
        }

def get_weights(pop,synapse_model,value):
    conns = nest.GetConnections(pop, synapse_model=synapse_model)
    conn_vals = nest.GetStatus(conns, [value])
    conn_vals = np.array(conn_vals)
    return conn_vals

def plot_weights(weights,title):
    reshaped = np.reshape(weights,(1,1))
    f = plt.figure()
    plt.imshow(reshaped,interpolation='none')
    plt.title(title)
    plt.colorbar()
    return f



def set_up_network():
   # The actual neuron population
    neuronpop = nest.Create("iaf_neuron", 1, params=ndict)

    # The background noise that will be connected with plastic synapses
    noise = nest.Create("poisson_generator", 1)
    nest.SetStatus(noise, {"rate": r_inp})
    # They need to be parroted to allow STDP
    inputs = nest.Create("parrot_neuron",1)
    nest.Connect(noise,inputs,{'rule':'one_to_one'})

    # Connect the parrots to the neuron via normal STDP synapse
    conn_dict = {"rule": "all_to_all"}
    syn_dict = {"model": "rstdp_synapse",
                "mu_plus":0.0,
                "mu_minus":0.0,
                "alpha": 1.0,
                "lambda": 0.001,
                "weight": epsc}
    nest.Connect(inputs, neuronpop, conn_dict, syn_dict)

    # Connect the parrots to the neuron via the RSTDP synapse
    conn_dict = {"rule": "all_to_all"}
    syn_dict = {"model": "stdp_synapse",
                "mu_plus":0.0,
                "mu_minus":0.0,
                "alpha": 1.0,
                "lambda": 0.001,
                "weight": epsc}
    nest.Connect(inputs, neuronpop, conn_dict, syn_dict)


    voltmeter = nest.Create("voltmeter")
    spikedetector = nest.Create("spike_detector")

    nest.SetStatus(voltmeter, {"withgid": True, "withtime": True})

    nest.Connect(neuronpop, spikedetector)
    nest.Connect(voltmeter, neuronpop)

    return inputs,neuronpop,voltmeter,spikedetector

if __name__ == '__main__':

    inputs, neuronpop, voltmeter, spikedetector = set_up_network()

    weights_before = {}
    weights_after = {}

    weights_before['stdp'] = get_weights(inputs,'stdp_synapse','weight')
    weights_before['rstdp'] = get_weights(inputs,'rstdp_synapse',
                                          'accumulation')
                                          # 'weight')

    # f = plot_weights(weights_before['stdp'],'stdp - before')
    # f = plot_weights(weights_before['rstdp'],'rstdp - before')
    # f.savefig('plots/'+run_str+'_before_weights.png')
    print weights_before

    nest.Simulate(t_sim)

    weights_after['stdp'] = get_weights(inputs,'stdp_synapse','weight')
    weights_after['rstdp'] = get_weights(inputs,'rstdp_synapse',
                                         # 'weight')
                                         'accumulation')

    # f = plot_weights(weights_after['stdp'],'stdp -after')
    # f = plot_weights(weights_after['rstdp'],'rstdp -after')
    # f.savefig('plots/'+run_str+'_weight_diff.png')
    # plt.figure()
    print weights_after


    nest.voltage_trace.from_device(voltmeter)
    nest.raster_plot.from_device(spikedetector, hist=True)
    plt.show()

