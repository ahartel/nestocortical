#include "logger.h"
#include "neuron.h"
#include "psp_event.h"

namespace xnet
{
/*
	void psp_event::processEvent()
	{
		LOGGER("Processing psp event for post-synaptic neuron " << post_neuron);
		Neuron* neuron = theSimulation.get_neuron_pointer(post_neuron);
		neuron->add_current_evolve(time,post_neuron,current);
	};
	*/
	Current_t psp_event::get_current() const
	{
		return current;
	}
}
