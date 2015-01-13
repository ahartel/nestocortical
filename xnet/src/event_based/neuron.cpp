#include <cmath>
#include "neuron.h"

namespace xnet
{
	Neuron::Neuron(Neuron_params const& p) :
		u(0),
		params(p),
		last_spike_time(0)
	{
	}

	bool Neuron::add_current_evolve(Time_t t, Id_t id, Current_t c)
	{
		bool fired = false;

		u += u*std::exp(-(t-last_spike_time)/params.tau_m) + c;
		if (u >= params.V_th)
		{
			// emit spike
			fired = true;
			// reset u
			u = 0;
		}

		return fired;
	}
}
