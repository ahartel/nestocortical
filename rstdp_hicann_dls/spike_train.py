"""Implementation of spike train tools. Including:
 * metric after Victor and Purpura.

Spike trains should have the format: list of tuples (neuron_id, time)."""

import unittest
import numpy as np

def vp_metric(train_a, train_b, cost):
    """My own implementation of the spike train metric after Victor and
    Purpura."""
    pass

def vp_metric_other(target, model, cost):
    """Method taken from
    http://www.cnbc.cmu.edu/~samondjm/papers/Aronov2003_pre.pdf"""
    # Let T and M be the number of spikes in the spiketrains _target_
    # and _model_.
    # _costs_ is a T+1 by M+1 numpy array that is initially set to zero.
    costs = np.zeros((len(target)+1, len(model)+1))
    # the first row and column are initialized to ascending integer values
    costs[0, :] = np.arange(len(model)+1)
    costs[:, 0] = np.arange(len(target)+1)
    # had to add the following two lines in order to support an empty target or
    # model spike train
    i = 0
    j = 0
    # iterate row-wise
    for i in range(1, len(target)+1):
        # iterate column-wise
        for j in range(1, len(model)+1):
            # q_factor = cost * abs(target[i-1] - model[j-1])
            # costs[i, j] = min([costs[i-1, j] + 1,
                               # costs[i, j-1] + 1,
                               # costs[i-1, j-1] + q_factor])
            # modified the previous line from this state:
            costs[i, j] = min([costs[i-1, j] + 1, costs[i, j-1] + 1, costs[i-1, j-1] + cost * abs(target[i-1] - model[j-1])])
    # print costs
    return costs[i, j]

def merge_spike_trains(train_a, train_b):
    pass

def generate_poisson_spike_train(neuron_id, rate):
    pass

def generate_linspace_spike_train(neuron_id, start, stop, num):
    return np.linspace(start, stop, num)

class vp_test_case(unittest.TestCase):
    """Test case for VP metric"""
    def test_equal(self):
        """This function applies some spike trains to the vp functions that
        should have zero distance."""
        a_train = [0.0, 1.0]
        b_train = [0.0, 1.0]
        for cost in np.arange(0.0, 10.0, 0.5):
            self.assertEqual(vp_metric_other(a_train, b_train, cost), 0)

    def test_shifted(self):
        """Take two equal spiketrains and shift one of them by q"""
        a_train = generate_linspace_spike_train(0, 0.0, 100.0, 21)
        T = len(a_train)
        for cost in np.arange(0.1, 1.0, 0.1):
            b_train = a_train + cost
            self.assertAlmostEqual(vp_metric_other(a_train, b_train, cost),
                                   cost*cost*T)

    def test_random(self):
        a_train = [183.0, 277.9, 390.2, 479.3, 564.3, 656.8, 781.3]
        b_train = [111.2, 171.7, 212.2, 269.0, 378.8, 460.5, 494.4, 541.1, 573.8, 648.1, 701.6, 762.2, 863.1]
        a_train = [183.0, 277.90000000000003, 390.19999999999999, 479.30000000000001, 564.30000000000007, 656.80000000000007, 781.30000000000007]
        b_train = [111.2, 171.70000000000002, 212.20000000000002, 269.0, 378.80000000000001, 460.5, 494.40000000000003, 541.10000000000002, 573.80000000000007, 648.10000000000002, 701.60000000000002, 762.20000000000005, 863.10000000000002]
        vp_metric_other(a_train, b_train, 10.0)

    def test_spike_count(self):
        """Compare a spike train with an empty spike train, such that the
        distance between both is the spike count of the non-empty spike
        train."""
        a_train = generate_linspace_spike_train(0, 0.0, 100.0, 22)
        T = len(a_train)
        b_train = []
        self.assertEqual(vp_metric_other(a_train, b_train, 0.0), T)

        a_train = []
        b_train = generate_linspace_spike_train(0, 0.0, 100.0, 22)
        M = len(a_train)
        self.assertEqual(vp_metric_other(a_train, b_train, 0.0), M)

if __name__ == '__main__':
    unittest.main()

