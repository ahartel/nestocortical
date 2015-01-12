#include "event_based/synapse.h"
#include "event_based/simulation_queue.h"

extern xnet::Simulation theSimulation;

namespace xnet
{
	//template <class WT>
	Synapse::Synapse(std::size_t pre, std::size_t post) :
		_delay(0),
		pre_neuron(pre),
		post_neuron(post)
	{
	}

	//template <class WT>
	void Synapse::generate_psp_event()
	{
		theSimulation.add_event(new psp_event(theSimulation.get_time(),post_neuron,_weight.calc_current()));
	}
}
