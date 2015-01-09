#include "event_based/logger.h"
#include "event_based/simulation_queue.h"

xnet::Simulation theSimulation;

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
		/* Create a population and a number of s neurons.
			The population represents the range of the
			then created neurons on the global neuron stack.
			Additionally, there is a SynapseRange object
			createrd for every neuron.
		*/
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
			auto p1_index = p1.get(i);
			// store synapse range in pre_syn_lookup
			pre_syn_lookup[p1_index].set_start(synapses.size());
			// iterate over target neurons
			for (unsigned int j=0; j<p2.size(); ++j)
			{
				synapses.push_back(Synapse(p1_index,p2.get(j)));
			}
			pre_syn_lookup[p1_index].set_end(synapses.size()-1);
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

	SynapseRange Simulation::get_synapse_range(Id_t const& neuron) const
	{
		return pre_syn_lookup[neuron];
	}

	Synapse* Simulation::get_synapse_pointer(Id_t const& synapse)
	{
		return &(synapses[synapse]);
	}

	Time_t Simulation::get_time() const
	{
		return time;
	}
}
