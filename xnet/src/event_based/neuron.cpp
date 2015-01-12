#include <cmath>
#include "neuron.h"
#include "event_based/simulation_queue.h"

extern xnet::Simulation theSimulation;

namespace xnet
{
	Neuron::Neuron(Neuron_params const& p) :
		u(0),
		params(p),
		last_spike_time(0)
	{
	}

	void Neuron::add_current_evolve(Time_t t, Id_t id, Current_t c)
	{
		u += u*std::exp(-(t-last_spike_time)/params.tau_m) + c;
		if (u >= params.V_th)
		{
			// emit spike
			theSimulation.add_event(new pre_syn_event(t,id));
			// reset u
			u = 0;
		}
	}
}
