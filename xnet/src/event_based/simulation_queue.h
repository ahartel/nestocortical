#pragma once
#include <queue>
#include "event_based/weight.h"
#include "event_based/neuron.h"
#include "event_based/synapse.h"
#include "event_based/population.h"
#include "event_based/synapse_range.h"
#include "event_based/event.h"
#include "event_based/pre_syn_event.h"
#include "event_based/post_syn_event.h"
#include "event_based/psp_event.h"

namespace xnet {
	class Simulation
	{
	public:
		Simulation () :
			time(0),
			eventQueue()
		{
		}
		void run();
		void scheduleEvent(event* newEvent)
		{
			eventQueue.push(newEvent);
		}
		Population create_population(std::size_t s);
		void connect_all_to_all_identical(Population& p1, Population& p2, Weight w);
		void add_event(event * e);
		void run_until_empty();
	protected:
		std::vector<Neuron> neurons;
		std::vector<Synapse> synapses;
		std::vector<SynapseRange> pre_syn_lookup;
		Time_t time;
		std::priority_queue<event*, std::vector<event*, std::allocator<event*> >,
			eventComparator> eventQueue;
	};
}
