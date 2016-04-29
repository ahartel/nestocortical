"""This module plots the data that has been saved from rstdp.py"""
SAVEFIG = True
if SAVEFIG:
    import matplotlib as mpl
    mpl.use('Agg')
import numpy as np
import pickle as pkl
import matplotlib.pyplot as plt
from rstdp import NUM_SYNAPSES, NUM_TGT_NEURONS, NUM_BG, EPSC

rewards = None
successes = None
mean_rewards = None
weight_diff_storage = None

def movingaverage (values, window):
    weights = np.repeat(1.0, window)/window
    sma = np.convolve(values, weights, 'valid')
    return sma

def plot_weights(weights, title=None):
    reshaped = np.reshape(weights, ((NUM_SYNAPSES-NUM_BG), NUM_TGT_NEURONS))
    f = plt.figure()
    plt.imshow(reshaped,interpolation='none')
    if not title is None:
        plt.title(title)
    plt.colorbar()
    return f

def plot_rates(rates):
    f = plt.figure()
    plt.title("Firing rates of "+str(NUM_TGT_NEURONS)+" neuron(s).")
    plt.xlabel("Run number")
    plt.ylabel("Firing rate [Hz]")
    for nrn in range(NUM_TGT_NEURONS):
        av = movingaverage(rates[:,nrn], 10)
        ax = plt.plot(np.arange(NUM_RUNS), rates[:, nrn], 'x')
        plt.plot(np.arange(NUM_RUNS)[NUM_RUNS-len(av):], av, '-',
                 color = ax[0].get_color())
    plt.grid()
    return f

def plot_rewards():
    global rewards
    global successes
    global mean_rewards

    f, axr = plt.subplots(1)
    plt.title("Reward and success evolution.")

    axr.plot(rewards, 'xb', label='reward')
    axr.plot(mean_rewards, '--b')
    axr.set_xlabel("Run number")
    axr.set_ylabel("Reward")
    axr.grid()

    axl = axr.twinx()
    axl.plot(successes, 'xr', label='success')
    # axl.axhline(np.mean(successes),linestyle='--',color='r')
    av = movingaverage(successes, 20)
    axl.plot(np.arange(NUM_RUNS)[NUM_RUNS-len(av):], av, '-r')
    axl.set_ylabel("Success")

    h1, l1 = axr.get_legend_handles_labels()
    h2, l2 = axl.get_legend_handles_labels()
    axr.legend(h1+h2, l1+l2, loc=1)

    return f

def evaluate_means(successes, weight_diff_storage,
                   start, stop):
    mean_success = np.mean(successes[start:stop])
    print "Mean success:", mean_success
    success_from_mean = successes[start:stop] - mean_success

    mean_eij = np.mean(weight_diff_storage[start:stop], 0)
    # print "Mean eligibility * mean success:", mean_eij * mean_success

    cov = 0
    for run in range(start, stop):
        cov += (successes[run] - mean_success) \
                * (weight_diff_storage[run] - mean_eij)
    cov /= float(NUM_RUNS)


    f, ax = plt.subplots(1, 2)
    ax[0].imshow(np.reshape(cov, ((NUM_SYNAPSES-NUM_BG), NUM_TGT_NEURONS)),
                 interpolation='none')
    ax[0].set_title("Covariance")
    ax[1].imshow(np.reshape(mean_eij * mean_success, ((NUM_SYNAPSES-NUM_BG),
                                                       NUM_TGT_NEURONS)),
                 vmin=np.min(cov),
                 vmax=np.max(cov),
                 interpolation='none')
    ax[1].set_title("Mean eij")
    PCM = ax[1].get_children()[2]
    plt.colorbar(PCM, ax=ax[1])
    plt.suptitle("Expected weight change between runs "+str(start) \
                +" and "+str(stop))
    if SAVEFIG:
        f.savefig("plots/mean_delta_w_"+str(start)+"_"+str(stop)+".png")


    return (np.reshape(cov, ((NUM_SYNAPSES-NUM_BG), NUM_TGT_NEURONS)),
            np.reshape(mean_eij, ((NUM_SYNAPSES-NUM_BG), NUM_TGT_NEURONS)))

def plot_spiketrains(trains):
    f = plt.figure()
    for nrn in range(NUM_TGT_NEURONS):
        plt.plot(trains[nrn], np.ones(len(trains[nrn]))*nrn, 'x')

    return f

if __name__ == '__main__':

    rates = pkl.load(open('data/firing_rates.pkl', 'r'))
    trains = pkl.load(open('data/spiketrains.pkl', 'r'))
    target = pkl.load(open('data/target_spiketrains.pkl', 'r'))
    rewards, successes, mean_rewards = pkl.load(open('data/rewards.pkl', 'r'))
    NUM_RUNS = len(rewards)
    weight_diff_storage = pkl.load(open('data/weight_diffs.pkl'))
    initial_weights = pkl.load(open("data/initial_weights.pkl"))
    target_weights = pkl.load(open("data/target_weights.pkl"))
    final_weights = pkl.load(open("data/final_weights.pkl"))

    f = plot_rates(rates)
    if SAVEFIG:
        f.savefig("plots/firing_rates.png")

    for run in np.linspace(0, NUM_RUNS-1, 10):
        print run
        fig = plot_spiketrains(trains[int(run)])
        if SAVEFIG is True:
            fig.savefig('plots/spiketrain_'+str(int(run))+'.png')

    f = plot_spiketrains(target)
    if SAVEFIG is True:
        f.savefig('plots/target_spiketrains.png')

    f = plot_rewards()
    if SAVEFIG:
        f.savefig("plots/rewards.png")

    # Data evaluation
    cov, mean_eij = evaluate_means(successes, weight_diff_storage,
                                   0, NUM_RUNS)
    evaluate_means(successes, weight_diff_storage,
                   0, NUM_RUNS/4)
    evaluate_means(successes, weight_diff_storage,
                   NUM_RUNS/4, NUM_RUNS/2)
    evaluate_means(successes, weight_diff_storage,
                   NUM_RUNS/2, NUM_RUNS/4*3)
    evaluate_means(successes, weight_diff_storage,
                   NUM_RUNS/4*3, NUM_RUNS)

    average_weight_diff = (final_weights-EPSC)/NUM_RUNS
    f = plot_weights(average_weight_diff, "Average weight change")
    if SAVEFIG:
        f.savefig("plots/average_weight_change.png")

    f = plot_weights(initial_weights, "Initial weights")
    if SAVEFIG:
        f.savefig("plots/initial_weights.png")

    f = plot_weights(target_weights, "target weights")
    if SAVEFIG:
        f.savefig("plots/target_weights.png")

    f = plot_weights(final_weights, "Final weights")
    if SAVEFIG:
        f.savefig("plots/final_weights.png")

    # print cov + mean_eij - average_weight_diff/NUM_RUNS

    if not SAVEFIG:
        plt.show()

