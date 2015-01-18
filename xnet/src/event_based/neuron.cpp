#include <cmath>
#include "neuron.h"
#include "logger.h"

namespace xnet
{
	Neuron::Neuron(Neuron_params const& p) :
		u(0),
		params(p),
		last_spike_time(0),
		last_update_time(0),
		last_inhibit_time(0),
		inhibited(false),
		refractory(false)
	{
	}

	bool Neuron::add_current_evolve(Time_t t, Current_t c)
	{
		bool fired = false;

		if ((!refractory || t > (last_spike_time + params.Tref))
			&& (!inhibited || t > (last_inhibit_time + params.Tinhibit)))
		{
			refractory = false;
			inhibited = false;
			u = u * std::exp(-1.0*float(t-last_update_time)/params.tau_mem) + c;
			LOGGER("c=" << c << ", u=" << u);

			if (u >= params.V_th)
			{
				// emit spike
				fired = true;
				refractory = true;
				// reset u
				u = 0;
				last_spike_time = t;
			}

			last_update_time = t;
		}

		return fired;
	}

	void Neuron::silence_neuron(Time_t t)
	{
		u = 0;
		last_inhibit_time = t;
		refractory = true;
	}
}
