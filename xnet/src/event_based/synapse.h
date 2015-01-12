#pragma once
#include <cstddef>
#include "weight.h"

namespace xnet {
	//template <class WT>
	class Synapse
	{
	public:
		Synapse(std::size_t pre, std::size_t post);
		void generate_psp_event();
	private:
		Id_t pre_neuron, post_neuron;
		//WT _weight;
		Weight _weight;
		Time_t _delay;
	};
}
