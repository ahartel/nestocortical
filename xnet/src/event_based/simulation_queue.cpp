#include "event_based/simulation_queue.h"

namespace xnet {
	void Simulation::run() {
		while (!eventQueue.empty()) {
			event * nextEvent = eventQueue.top();
			eventQueue.pop();
			time = nextEvent->time;
			nextEvent->processEvent();
			delete nextEvent;
		}
	}

	Population Simulation::create_population(std::size_t s)
	{
		Population pop;
		pop.set_start(neurons.size());
		for (unsigned int i=0;i<s;++i)
		{
			neurons.push_back(Neuron());
			pre_syn_lookup.push_back({});
		}
		pop.set_end(neurons.size()-1);
		return pop;
	}

	void Simulation::connect_all_to_all_identical(Population& p1, Population& p2, Weight w)
	{
		// iterate over source neurons
		for (unsigned int i=0; i<p1.size(); ++i)
		{
			// store synapse range in pre_syn_lookup
			pre_syn_lookup[p1.get(i)].set_start(synapses.size());
			// iterate over target neurons
			for (unsigned int j=0; j<p2.size(); ++j)
			{
				synapses.push_back(Synapse(p1.get(i),p2.get(j)));
			}
			pre_syn_lookup[p1.get(i)].set_end(synapses.size());
		}
	}

	void Simulation::add_event(event * e)
	{
		eventQueue.push(e);
	}

	void Simulation::run_until_empty()
	{
		run();
	}
}
