#include "logger.h"
#include "pre_syn_event.h"
#include "simulation_queue.h"
#include "synapse_range.h"

extern xnet::Simulation theSimulation;

namespace xnet
{
	void pre_syn_event::processEvent()
	{
		LOGGER("Processing pre_syn_event.");
		SynapseRange synrange = theSimulation.get_synapse_range(pre_neuron);
		for (std::size_t i=synrange.begin();i<synrange.end();++i)
		{
			Synapse* syn = theSimulation.get_synapse_pointer(i);
			syn->generate_psp_event();
		}
	};
}
