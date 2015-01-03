#include "event_based/neuron.h"
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
		Population pop(object_counter);
		for (unsigned int i=0;i<s;++i)
		{
			neurons.push_back(Neuron());
			//Population.push(&(neurons.back()));
			++object_counter;
		}
		pop.set_end(object_counter-1);
		return pop;
	}

	void Simulation::connect_all_to_all(Population& p1, Population& p2)
	{
		for (unsigned int i=0; i<p1.size(); ++i)
		{
			for (unsigned int j=0; j<p2.size(); ++j)
			{
				synapses.push_back(Synapse(p1.get(i),p2.get(j)));
			}
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
