#include "event_based/synapse.h"

namespace xnet
{
	//template <class WT>
	Synapse::Synapse(std::size_t pre, std::size_t post, Weight const& w, bool hard_inhibit) :
		_delay(0),
		pre_neuron(pre),
		post_neuron(post),
		_weight(w),
		hard(hard_inhibit)
	{
	}

	//template <class WT>
	/*
	psp_event* Synapse::generate_psp_event()
	{
		return new psp_event(theSimulation.get_time(),post_neuron,_weight.calc_current());
	}
	*/

	Id_t Synapse::get_post_neuron() const
	{
		return post_neuron;
	}

	Current_t Synapse::get_current() const
	{
		return _weight.calc_current();
	}

	bool Synapse::hard_inhibit() const
	{
		return hard;
	}
}
