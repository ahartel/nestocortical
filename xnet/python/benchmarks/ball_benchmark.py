import os
import cPickle
import numpy as np
import neuroplotlib as nplt
from benchmark import Benchmark
import matplotlib.pyplot as plt

class BallBenchmark(Benchmark):
    def __init__(self,repetitions,threads=1):
        Benchmark.__init__(self,repetitions,threads)
        self.psth = {}
        self.metrics = {}
        self.neurons = range(512,560)

    def post_process(self,run):
        if not self.has_postprocessed[run]:
            print "Post-processing run",run
            # load order
            stimuli = np.loadtxt('./results/'+run+'/xnet_balls_order',delimiter=',')
            # load spikes
            data = np.loadtxt('./results/'+run+'/xnet_balls_spikes.dat', delimiter=',')

            # generate Peri-Stimulus Time Histogram
            self.psth[run] = nplt.psth.psth(stimuli, data, self.neurons, 10)

            self.has_postprocessed[run] = True
        else:
            print "Skipping post-processing of run",run

    def evaluate(self,run):
        print "Evaluating run",run
        stim_count = 0
        self.metrics[run] = {}
        for stimulus,groups in self.psth[run].iteritems():
            self.metrics[run][stimulus] = []
            # calculate specialization value
            #if stim_count == 0:
            #    print stimulus," ",len(groups)
            for group in groups:
                #if stim_count == 0:
                #    print "==group=="
                metric = 0
                for nrn,times in group.iteritems():
                    std = np.std(times)
                    num = float(len(times))
                    #if stim_count == 0:
                    #    print " ",nrn," ",num," ",std
                    metric += num/(std+0.001)

                metric /= len(group)
                self.metrics[run][stimulus].append(metric)

            stim_count += 1

        return self.metrics

    def plot_performance(self):
        for ii,run in enumerate(self.get_runs()):
            plt.subplot(len(self.get_runs()),1,ii)
            plt.ylabel(run)
            for stim in self.metrics[run].itervalues():
                plt.plot(stim[:-1])
            plt.grid()

    def save(self):
        with open('./benchmark_state.pkl','wb') as output:
            cPickle.dump(self,output)

    @classmethod
    def check_and_load_state(cls,num_repetitions):
        if os.path.isfile('benchmark_state.pkl'):
            print "Loading ./benchmark_state.pkl"
            obj = cls(num_repetitions)
            with open('./benchmark_state.pkl','rb') as inf:
                loaded = cPickle.load(inf)
                for name,call in loaded.get_runs().iteritems():
                    obj.append(name,call,loaded.has_run[name],loaded.has_postprocessed[name])
                    obj.psth[name] = loaded.psth[name]

            return obj
        else:
            return cls(num_repetitions)

