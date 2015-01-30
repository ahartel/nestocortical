import os
import cPickle

class Benchmark:
    def __init__(self,repetitions,threads=1):
        self.runs = {}
        self.has_run = {}
        self.has_postprocessed = {}
        self.num_rep = repetitions
        self.num_threads = threads

        if not os.path.exists('results'):
            os.makedirs('results')

    def get_run_string(self,run):
        return self.runs[run]+" "+str(self.num_rep)+' '+os.getcwd()+'/results/'+run

    def get_runs(self):
        return self.runs

    def run(self,run):
        if not self.has_run[run]:
            if not os.path.exists('results/'+run):
                os.makedirs('results/'+run)

            run_str = self.get_run_string(run)
            print "Running ",run," with call ",run_str
            os.system(run_str)

            self.has_run[run] = True
        else:
            print "Not running ",run

    def post_process(self,run):
        pass

    def evaluate(self):
        pass

    def evaluate_all(self):
        ret = {}
        for run in self.runs:
            self.run(run)
            self.post_process(run)
            ret[run] = self.evaluate(run)

        return ret

    def append(self,key,call,hasrun=False,haspost=False):
        if self.runs.has_key(key):
            raise KeyError('The experiment alias '+key+' already exists.')
        else:
            self.runs[key] = call
            self.has_run[key] = hasrun
            self.has_postprocessed[key] = haspost

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

            return obj
        else:
            return cls(num_repetitions)

