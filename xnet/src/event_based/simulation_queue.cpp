#include "event_based/logger.h"
#include "event_based/simulation_queue.h"

xnet::Simulation theSimulation;

namespace xnet {

	void Simulation::run() {
		while (!eventQueue.empty()) {
			event * nextEvent = eventQueue.top();
			eventQueue.pop();
			time = nextEvent->time;
			//nextEvent->processEvent();
			processEvent(nextEvent);
			delete nextEvent;
		}
	}

	void Simulation::processEvent(event* ev) {
		auto type = ev->get_type();
		Id_t linked_object = ev->get_linked_object_id();
		if (type == EventType::PRE)
		{
			// add this spike to the global spike list
			add_spike(time,linked_object);
			// check if there are post-synaptic neurons to this neuron
			SynapseRange synrange = get_synapse_range(linked_object);
			if (synrange.non_empty())
			{
				LOGGER("Processing pre_syn_event for neuron " << linked_object << " and synrange from "<< synrange.begin() << " to " << synrange.end());
				for (std::size_t i=synrange.begin();i<synrange.end();++i)
				{
					Synapse* syn = get_synapse_pointer(i);
					add_event(new psp_event(time,syn->get_post_neuron(),syn->get_current()));
				}
			}
			else
				LOGGER("Processing pre_syn_event for neuron. Empty, not doing anything.");
		}
		else if (type == EventType::PSP)
		{
			psp_event* psp_evt = static_cast<psp_event*>(ev);

			LOGGER("Processing psp event for post-synaptic neuron " << linked_object);
			Neuron* neuron = get_neuron_pointer(linked_object);
			bool fired = neuron->add_current_evolve(time,linked_object,psp_evt->get_current());
			if (fired)
			{
				add_event(new pre_syn_event(time,linked_object));
			}
		}
		//	case EventType::PST:
		//	break;
		//	case EventType::SIL:
		//	break;
		//}
	}

	Population Simulation::create_population_start()
	{
		Population pop;
		pop.set_start(neurons.size());
		return pop;
	}

	void Simulation::create_population_add_neuron(Neuron_params const& p)
	{
		neurons.push_back(Neuron(p));
		pre_syn_lookup.push_back({});
	}

	Population Simulation::create_population_fixed(std::size_t s, Neuron_params const& params)
	{
		/* Create a population and a number of s neurons.
			The population represents the range of the
			then created neurons on the global neuron stack.
			Additionally, there is a SynapseRange object
			createrd for every neuron.
		*/
		Population pop = create_population_start();
		for (unsigned int i=0;i<s;++i)
		{
			create_population_add_neuron(params);
		}
		pop.set_end(neurons.size()-1);
		return pop;
	}

	Population Simulation::create_population_uniform(std::size_t s, Membrane_t th_high, Membrane_t th_low, Timeconst_t tm_low, Timeconst_t tm_high)
	{
		/* Create a population and a number of s neurons.
			The population represents the range of the
			then created neurons on the global neuron stack.
			Additionally, there is a SynapseRange object
			createrd for every neuron.
		*/
		std::uniform_real_distribution<Membrane_t> V_th(th_low,th_high);
		std::uniform_real_distribution<Timeconst_t> tau_m(tm_low,tm_high);
		Population pop = create_population_start();
		for (unsigned int i=0;i<s;++i)
		{
			create_population_add_neuron({V_th(generator),tau_m(generator)});
		}
		pop.set_end(neurons.size()-1);
		return pop;
	}

	Population Simulation::create_population_normal(std::size_t s, Membrane_t th_mean, Membrane_t th_std, Timeconst_t tm_mean, Timeconst_t tm_std)
	{
		/* Create a population and a number of s neurons.
			The population represents the range of the
			then created neurons on the global neuron stack.
			Additionally, there is a SynapseRange object
			createrd for every neuron.
		*/
		std::normal_distribution<Membrane_t> V_th(th_mean,th_std);
		std::normal_distribution<Timeconst_t> tau_m(tm_mean,tm_std);
		Population pop = create_population_start();
		for (unsigned int i=0;i<s;++i)
		{
			create_population_add_neuron({V_th(generator),tau_m(generator)});
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

	Neuron* Simulation::get_neuron_pointer(Id_t const& nrn)
	{
		return &(neurons[nrn]);
	}

	Time_t Simulation::get_time() const
	{
		return time;
	}

	std::vector<Spike_t>& Simulation::get_spikes()
	{
		return spike_list;
	}

	void Simulation::add_spike(Time_t t, Id_t nrn)
	{
		spike_list.push_back(std::make_tuple(t,nrn));
	}
}
