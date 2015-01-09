#include "event_based/synapse.h"
#include "event_based/simulation_queue.h"

extern xnet::Simulation theSimulation;

namespace xnet
{
	Synapse::Synapse(std::size_t pre, std::size_t post) :
		_delay(0)
	{
	}

	void Synapse::generate_psp_event()
	{
		theSimulation.add_event(new psp_event(theSimulation.get_time(),/*neuron*/,_weight.calc_current()));
	}
}
