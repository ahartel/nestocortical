#pragma once
#include "xnet_types.h"
#include "neuron_params.h"

namespace xnet {
	class Neuron
	{
	public:
		Neuron(Neuron_params const& p);
		void add_current_evolve(Time_t t, Id_t id, Current_t c);
	private:
		Membrane_t u;
		Neuron_params params;
		Time_t last_spike_time;
	};
}
