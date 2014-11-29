#include "synapse.h"
#include "neuron.h"

#include <sstream>

namespace xnet {

	void Synapse::pre(Time_t t)
	{
		last_pre_spike = t;
		neurons->evolve(psn,w,t);
	}
	//	def pre(self,t):
	//		#print 'sending spike to neuron ',self.__psn,' with weight ',self.__w
	//		self.__last_pre_spike = t
	//		self.__neurons.evolve(self.__psn,self.__w,t)

	void Synapse::register_at_neuron()
	{
		neurons->register_synapse(psn, this);
	}
	//	def register_at_neuron(self):
	//		self.__neurons.register_synapse(self.__psn,self.update)

	void dump_weights(SynapseArray const& synapses, string filename, size_t num_neurons, size_t num_inputs)
	{
		// write weights to a file with one line per line of weights in the image
		// one neuron gets image_height lines with image_width entries
		// after the lines of one neuron have been written, the next neuron starts immediately
		vector<vector<float>> neuron_weights(num_neurons);
		for (int n=0; n<num_inputs; ++n)
		{
			for (int i=0; i<num_neurons; ++i)
			{
				neuron_weights[i].push_back(synapses[n][i].get_weight());
			}
		}
		unsigned int cnt = 0;
		for (auto neuron : neuron_weights)
		{
			stringstream ss("");
			ss << filename << cnt++;
			ofstream weight_file(ss.str(),ios::out);
			weight_file << fixed << setprecision(2);

			for (int i=0; i<num_inputs-1; ++i) {
				weight_file << neuron[i] << " ";
			}
			weight_file << neuron[num_inputs-1];

			weight_file.close();
		}
	}
}
