#pragma once
#include "xnet_types.h"
#include "neuron_params.h"

namespace xnet {
	class Neuron
	{
	public:
		Neuron(Neuron_params const& p);
		bool add_current_evolve(Time_t t, Current_t c);
	private:
		Membrane_t u;
		Neuron_params params;
		Time_t last_spike_time;
	};
}
