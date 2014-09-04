#include "neuron.h"
#include "synapse.h"

void Neurons::update_synapses(int neuron_number, Time_t t)
{
	cout << "Updating synapses of neuron #" << neuron_number << " @time " << t << endl;
	for (auto syn : this->synapses[neuron_number])
		syn->update(t);
}
