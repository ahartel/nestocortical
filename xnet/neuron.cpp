#include "neuron.h"
#include "synapse.h"

namespace xnet {

	void Neurons::update_synapses(int neuron_number, Time_t t)
	{
#ifdef DEBUG_OUTPUT
		cout << "Updating synapses of neuron #" << neuron_number << " @time " << t << endl;
		//cout << synapses[19].back()->get_id() << endl;
#endif
		for (int i=0; i<num_synapses; ++i)
			synapses[neuron_number][i]->update(t);
	}

	void Neurons::register_synapse(unsigned int neuron, Synapse* synapse)
	{
		//if (neuron == 19)
		//	cout << "Registering synapse " << synapse->get_id() << " for neuron " << neuron << endl;
		//cout << synapse_count[neuron] << endl;
		synapses[neuron][synapse_count[neuron]++] = synapse;
	}

	Synapse** Neurons::get_synapses(int neuron) const
	{
		//cout << synapses[0].back()->get_psn() << endl;
		return synapses[neuron];
	}

	void Neurons::evolve(int neuron_number, float weight, Time_t t)
	{
		if (t > (*max_element(tlast_spike.begin(),tlast_spike.end()) + Tinhibit) || t < EPSILON)
		{
			float last_spike = tlast_spike[neuron_number];
			if (((t-last_spike) > Trefrac) || t < EPSILON)
			{
				float last_t = tlast_update[neuron_number];
				float last_u = u[neuron_number];
				u[neuron_number] = last_u*exp(-(t-last_t)/tau) + weight;
				tlast_update[neuron_number] = t;

				if (u[neuron_number] > Vt)
				{
					tlast_spike[neuron_number] = t;
					spikes.push_back(make_tuple(neuron_number,t));
					update_synapses(neuron_number,t);
					for (int n=0; n < num_neurons; ++n)
						u[n] = 0;
				}
			}
			if (this->record_membrane)
				this->membrane_record[neuron_number].push_back(make_tuple(t,this->u[neuron_number],weight));
		}
	}
}
