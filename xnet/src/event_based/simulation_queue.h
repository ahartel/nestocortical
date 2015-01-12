#pragma once
#include <queue>
#include <random>
#include "event_based/weight.h"
#include "event_based/neuron.h"
#include "event_based/neuron_params.h"
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
		Population create_population_start();
		void create_population_add_neuron(Neuron_params const& p);
		Population create_population_fixed(std::size_t s, Neuron_params const& params);
		Population create_population_uniform(std::size_t s, Membrane_t th_high, Membrane_t th_low, Timeconst_t tm_low, Timeconst_t tm_high);
		Population create_population_normal(std::size_t s, Membrane_t th_mean, Membrane_t th_std, Timeconst_t tm_mean, Timeconst_t tm_std);
		void connect_all_to_all_identical(Population& p1, Population& p2, Weight w);
		void add_event(event * e);
		void run_until_empty();
		SynapseRange get_synapse_range(Id_t const& neuron) const;
		Synapse* get_synapse_pointer(Id_t const& synapse);
		Neuron* get_neuron_pointer(Id_t const& nrn);
		Time_t get_time() const;
		void add_spike(Time_t t, Id_t nrn);
		std::vector<Spike_t>& get_spikes();
	protected:
		std::default_random_engine generator;
		std::vector<Neuron> neurons;
		std::vector<Synapse> synapses;
		std::vector<SynapseRange> pre_syn_lookup;
		Time_t time;
		std::priority_queue<event*, std::vector<event*, std::allocator<event*> >,
			eventComparator> eventQueue;
		std::vector<Spike_t> spike_list;
	};
}
