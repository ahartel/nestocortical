#include "logger.h"
#include "pre_syn_event.h"
#include "synapse_range.h"

namespace xnet
{
/*
	void pre_syn_event::processEvent()
	{
		// add this spike to the global spike list
		theSimulation.add_spike(time,pre_neuron);
		// check if there are post-synaptic neurons to this neuron
		SynapseRange synrange = theSimulation.get_synapse_range(pre_neuron);
		if (synrange.non_empty())
		{
			LOGGER("Processing pre_syn_event for neuron " << pre_neuron << " and synrange from "<< synrange.begin() << " to " << synrange.end());
			for (std::size_t i=synrange.begin();i<synrange.end();++i)
			{
				Synapse* syn = theSimulation.get_synapse_pointer(i);
				syn->generate_psp_event();
			}
		}
		else
			LOGGER("Processing pre_syn_event for neuron. Empty, not doing anything.");
	};
	*/
}
