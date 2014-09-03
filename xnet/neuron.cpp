#include "neuron.h"
#include "synapse.h"

void Neurons::update_synapses(int neuron_number, Time_t t)
{
	for (auto syn : this->synapses[neuron_number])
		syn->update(t);
}
