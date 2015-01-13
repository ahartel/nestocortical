#pragma once
#include <cstddef>
#include "weight.h"
#include "psp_event.h"

namespace xnet {
	//template <class WT>
	class Synapse
	{
	public:
		Synapse(std::size_t pre, std::size_t post, Weight const& w);
		//psp_event* generate_psp_event();
		Id_t get_post_neuron() const;
		Current_t get_current() const;
	private:
		Id_t pre_neuron, post_neuron;
		//WT _weight;
		Weight _weight;
		Time_t _delay;
	};
}
