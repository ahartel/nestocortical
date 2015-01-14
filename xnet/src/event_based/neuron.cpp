#include <cmath>
#include "neuron.h"
#include "logger.h"

namespace xnet
{
	Neuron::Neuron(Neuron_params const& p) :
		u(0),
		params(p),
		last_spike_time(0)
	{
	}

	bool Neuron::add_current_evolve(Time_t t, Current_t c)
	{
		bool fired = false;

		LOGGER("c=" << c << ", u=" << u);
		u = u * std::exp(-1.0*(float(t-last_spike_time)/params.tau_mem)) + c;
		LOGGER("c=" << c << ", u=" << u);

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
