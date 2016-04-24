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
    costs[0, :] = np.arange(len(model)+1)
    costs[:, 0] = np.arange(len(target)+1)
    for i in range(1, len(target)+1):
        # had to add the following line in order to support an empty model
        # spike train
        j = 0
        for j in range(1, len(model)+1):
            q_factor = cost * abs(target[i-1] - model[j-1])
            costs[i, j] = min([costs[i-1, j] + 1,
                               costs[i, j-1] + 1,
                               costs[i-1, j-1] + q_factor])
            # modified the previous line from this state:
            # costs[i, j] = min([costs[i-1, j] + 1, costs[i, j-1] + 1, costs[i-1, j-1] + q * abs(target[i-1] - model[j-1])])
    # print costs
    return costs[i, j]

def merge_spike_trains(train_a, train_b):
    pass

def generate_poisson_spike_train(neuron_id, rate):
    pass

def generate_linspace_spike_train(neuron_id, start, stop, diff):
    return np.linspace(start, stop, diff)

class IntegerArithmeticTestCase(unittest.TestCase):
    def testAdd(self):  ## test method names begin 'test*'
        self.assertEqual((1 + 2), 3)
        self.assertEqual(0 + 1, 1)
    def testMultiply(self):
        self.assertEqual((0 * 10), 0)
        self.assertEqual((5 * 8), 40)


class vpTestCase(unittest.TestCase):
    """Test case for VP metric"""
    def testEqual(self):
        """This function applies some spike trains to the vp functions that
        should have zero distance."""
        a_train = [0.0, 1.0]
        b_train = [0.0, 1.0]
        self.assertEqual(vp_metric_other(a_train, b_train, 10), 0)

    def testShifted(self):
        """Take two equal spiketrains and shift one of them by q"""
        cost = 1.0
        a_train = generate_linspace_spike_train(0, 0.0, 100.0, 22.0)
        T = len(a_train)
        b_train = a_train + cost
        self.assertEqual(vp_metric_other(a_train, b_train, cost), cost*T)

    def testSpikeCount(self):
        a_train = generate_linspace_spike_train(0, 0.0, 100.0, 22.0)
        T = len(a_train)
        b_train = []
        self.assertEqual(vp_metric_other(a_train, b_train, 0.0), T)

if __name__ == '__main__':
    unittest.main()

