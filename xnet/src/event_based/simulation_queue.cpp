#include <fstream>
#include <tuple>
#include <sstream>
#include "event_based/logger.h"
#include "event_based/simulation_queue.h"

namespace xnet {

	template<typename SYN, typename WT>
	SimulationQueue<SYN,WT>::SimulationQueue () :
			number_of_neurons(0),
			cache_valid_time(0),
			cache_dirty(false),
			time(0),
			eventQueue(),
			last_spike_fetched(0)
		{
		}

	template<typename SYN, typename WT>
	void SimulationQueue<SYN,WT>::run_one_event()
	{
		//LOGGER("eventQueue size: " << eventQueue.size());
		event * nextEvent = eventQueue.top();
		eventQueue.pop();
		time = nextEvent->time;
		//nextEvent->processEvent();
		processEvent(nextEvent);
		delete nextEvent;
		//LOGGER("eventQueue size: " << eventQueue.size());
	}

	template<typename SYN, typename WT>
	void SimulationQueue<SYN,WT>::run(size_t num) {
		for (unsigned int i=0; i<num; ++i)
		{
			if (!eventQueue.empty())
				run_one_event();
		}
	}

	template<typename SYN, typename WT>
	void SimulationQueue<SYN,WT>::flush_psp_cache()
	{
		LOGGER("Flushing psp cache");
		if (cache_dirty)
		{
			for (std::map<Id_t,Current_t>::iterator it=psp_cache.begin(); it!=psp_cache.end(); ++it)
			{
				add_event(new psp_event(cache_valid_time,it->first,it->second));
			}
			psp_cache.clear();
			cache_dirty = false;
		}
	}

	template<typename SYN, typename WT>
	inline
	void SimulationQueue<SYN,WT>::add_psp_cache(Id_t neuron, Current_t current)
	{
		psp_cache[neuron] += current;
		cache_dirty = true;
		cache_valid_time = time;
	}

	template<typename SYN, typename WT>
	void SimulationQueue<SYN,WT>::processEvent(event* ev) {
		auto type = ev->get_type();
		Id_t linked_object = ev->get_linked_object_id();
		if (type == EventType::PRE)
		{
			if (time > cache_valid_time)
				flush_psp_cache();

			// add this spike to the global spike list
			add_spike(time,linked_object);
			// check if there are post-synaptic neurons to this neuron
			for (SynapseRange synrange : get_synapse_ranges(linked_object))
			{
				if (synrange.non_empty())
				{
					LOGGER("@" << time << " Processing pre_syn_event for neuron " << linked_object << " and synrange from "<< synrange.begin() << " to " << synrange.end());
					for (std::size_t i=synrange.begin(); i<=synrange.end(); ++i)
					{
						SYN* syn = get_synapse_pointer(i);
						if (syn->hard_inhibit())
							add_event(new silence_event(time,syn->get_post_neuron()));
						else
						{
							Current_t current = syn->eval_pre_event(time);
							LOGGER("Current: " << current);
							add_psp_cache(syn->get_post_neuron(),current);
						}
					}
				}
				else
					LOGGER("@" << time << " Processing pre_syn_event for neuron. Empty, not doing anything.");
		}
		}
		else if (type == EventType::PSP)
		{
			flush_psp_cache();

			psp_event* psp_evt = static_cast<psp_event*>(ev);

			LOGGER("@" << time << " Processing psp event for post-synaptic neuron " << linked_object);
			Neuron* neuron = get_neuron_pointer(linked_object);
			bool fired = neuron->add_current_evolve(time,psp_evt->get_current());
			if (fired)
			{
				LOGGER("Neuron " << linked_object << " fired with delay " << neuron->get_delay());
				add_event(new pre_syn_event(time+neuron->get_delay(),linked_object));
				add_event(new post_syn_event(time,linked_object));
			}
		}
		else if (type == EventType::PST)
		{
			flush_psp_cache();

			for (Id_t syn_id : get_pre_synapse_ranges(linked_object))
			{
				LOGGER("@" << time << " Processing post_syn_event for neuron " << linked_object << " and synapse "<< syn_id);
				SYN* syn = get_synapse_pointer(syn_id);
				if (syn->hard_inhibit())
				{} // pass
				else
					syn->eval_post_event(time);
			}
		}
		else if (type == EventType::SIL)
		{
			flush_psp_cache();

			LOGGER("@" << time << " Processing silence event for post-synaptic neuron " << linked_object);
			Neuron* neuron = get_neuron_pointer(linked_object);
			neuron->silence_neuron(time);
		}
	}

	template<typename SYN, typename WT>
	inline
	Population SimulationQueue<SYN,WT>::create_population_start(std::size_t size)
	{
		LOGGER("Creating population of size " << size << " starting at " << neurons.size());
		Population pop;
		pop.set_start(neurons.size());
		return pop;
	}

	template<typename SYN, typename WT>
	void SimulationQueue<SYN,WT>::create_population_add_neuron(Neuron_params const& p)
	{
		neurons.push_back(Neuron(p));
		number_of_neurons += 1;
		pre_syn_lookup.push_back({});
		post_syn_lookup.push_back({});
	}

	template<typename SYN, typename WT>
	Population SimulationQueue<SYN,WT>::create_population_fixed(std::size_t s, Neuron_params const& params)
	{
		/* Create a population and a number of s neurons.
			The population represents the range of the
			then created neurons on the global neuron stack.
			Additionally, there is a SynapseRange object
			createrd for every neuron.
		*/
		Population pop = create_population_start(s);
		for (unsigned int i=0;i<s;++i)
		{
			create_population_add_neuron(params);
		}
		pop.set_end(neurons.size()-1);
		return pop;
	}

	template<typename SYN, typename WT>
	Population SimulationQueue<SYN,WT>::create_population_uniform(
		std::size_t s,
		UniformRange_t th,
		UniformRange_t tm,
		UniformRange_t tr,
		UniformRange_t ti,
		UniformRange_t td)
	{
		/* Create a population and a number of s neurons.
			The population represents the range of the
			then created neurons on the global neuron stack.
			Additionally, there is a SynapseRange object
			createrd for every neuron.
		*/
		std::uniform_real_distribution<Membrane_t> V_th(th.low(),th.high());
		std::uniform_real_distribution<Timeconst_t> tau_mem(tm.low(),tm.high());
		std::uniform_int_distribution<Time_t> tau_ref(tr.low(),tr.high());
		std::uniform_int_distribution<Time_t> Tinhibit(ti.low(),ti.high());
		std::uniform_int_distribution<Time_t> Tdelay(td.low(),td.high());

		Population pop = create_population_start(s);
		for (unsigned int i=0;i<s;++i)
		{
			create_population_add_neuron({
									V_th(generator),
									tau_mem(generator),
									tau_ref(generator),
									Tinhibit(generator)
								});
		}
		pop.set_end(neurons.size()-1);
		return pop;
	}

	template<typename SYN, typename WT>
	Population SimulationQueue<SYN,WT>::create_population_normal(
		std::size_t s,
		NormalRange_t th,
		NormalRange_t tm,
		NormalRange_t tr,
		NormalRange_t ti,
		NormalRange_t td)
	{
		/* Create a population and a number of s neurons.
			The population represents the range of the
			then created neurons on the global neuron stack.
			Additionally, there is a SynapseRange object
			createrd for every neuron.
		*/
		std::normal_distribution<Membrane_t> V_th(th.mean(),th.std());
		std::normal_distribution<Timeconst_t> tau_mem(tm.mean(),tm.std());
		std::normal_distribution<Realtime_t> tau_ref(tr.mean(),tr.std());
		std::normal_distribution<Realtime_t> Tinhibit(ti.mean(),ti.std());
		std::normal_distribution<Realtime_t> Tdelay(td.mean(),td.std());

		Population pop = create_population_start(s);
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wnarrowing"
		for (unsigned int i=0;i<s;++i)
		{
			create_population_add_neuron({
									V_th(generator),
									tau_mem(generator),
									tau_ref(generator),
									Tinhibit(generator),
									Tdelay(generator)
								});
		}
#pragma GCC diagnostic pop
		pop.set_end(neurons.size()-1);
		return pop;
	}

	template<typename SYN, typename WT>
	void SimulationQueue<SYN,WT>::connect_all_to_all_identical(
		Population const& p1,
		Population const& p2,
		WT const& w,
		Timeconst_t ltp)
	{
		LOGGER("Connecting Population ("<<p1.begin()<<"-"<<p1.end()<<") to population ("<<p2.begin()<<"-"<<p2.end()<<") all-to-all");
		// iterate over source neurons
		for (unsigned int i=0; i<p1.size(); ++i)
		{
			auto p1_index = p1.get(i);
			// store synapse range in pre_syn_lookup
			SynapseRange range(synapses.size());
			pre_syn_lookup[p1_index].push_back(range);
			// iterate over target neurons
			for (unsigned int j=0; j<p2.size(); ++j)
			{
				Id_t post = p2.get(j);
				add_synapse(p1_index,post,w,ltp);
			}
			pre_syn_lookup[p1_index].back().set_end(synapses.size()-1);
		}
	}

	template<typename SYN, typename WT>
	void SimulationQueue<SYN,WT>::connect_one_to_one_identical(
		Population const& p1,
		Population const& p2,
		WT const& w,
		Timeconst_t ltp)
	{
		if (p1.size() != p2.size())
			throw std::out_of_range("Populations mus be of equal size in SimulationQueue::connect_one_to_one_identical");

		LOGGER("Connecting Population ("<<p1.begin()<<"-"<<p1.end()<<") to population ("<<p2.begin()<<"-"<<p2.end()<<") one-to-one");
		// iterate over source neurons
		for (unsigned int i=0; i<p1.size(); ++i)
		{
			auto p1_index = p1.get(i);
			// store synapse range in pre_syn_lookup
			SynapseRange range(synapses.size());
			pre_syn_lookup[p1_index].push_back(range);

			Id_t post = p2.get(i);
			add_synapse(p1_index,post,w,ltp);

			pre_syn_lookup[p1_index].back().set_end(synapses.size()-1);
		}
	}

	template<typename SYN, typename WT>
	void SimulationQueue<SYN,WT>::connect_all_to_all_wta(Population const& p)
	{
		// iterate over source neurons
		for (unsigned int i=0; i<p.size(); ++i)
		{
			auto p1_index = p.get(i);
			// store synapse range in pre_syn_lookup
			SynapseRange range(synapses.size());
			pre_syn_lookup[p1_index].push_back(range);
			// iterate over target neurons
			for (unsigned int j=0; j<p.size(); ++j)
			{
				if (i!=j)
					synapses.push_back(SYN(p1_index,p.get(j),WT({}),0,true));
			}
			pre_syn_lookup[p1_index].back().set_end(synapses.size()-1);
		}
	}

	template<typename SYN, typename WT>
	void SimulationQueue<SYN,WT>::connect_all_to_all_normal(
		Population const& p1,
		Population const& p2,
		NormalRange_t wmin,
		NormalRange_t wmax,
		NormalRange_t winit,
		NormalRange_t ap,
		NormalRange_t am,
		NormalRange_t ltp
	)
	{
		LOGGER("Connecting Population ("<<p1.begin()<<"-"<<p1.end()<<") to population ("<<p2.begin()<<"-"<<p2.end()<<")");
		// distributions to sample from
		std::normal_distribution<Current_t> wmin_dist(wmin.mean(),wmin.std());
		std::normal_distribution<Current_t> wmax_dist(wmax.mean(),wmax.std());
		std::normal_distribution<Current_t> winit_dist(winit.mean(),winit.std());
		std::normal_distribution<Current_t> ap_dist(ap.mean(),ap.std());
		std::normal_distribution<Current_t> am_dist(am.mean(),am.std());
		std::normal_distribution<Timeconst_t> ltp_dist(ltp.mean(), ltp.std());

		// iterate over source neurons
		for (unsigned int i=0; i<p1.size(); ++i)
		{
			auto p1_index = p1.get(i);
			// store synapse range in pre_syn_lookup
			SynapseRange range(synapses.size());
			pre_syn_lookup[p1_index].push_back(range);
			// iterate over target neurons
			for (unsigned int j=0; j<p2.size(); ++j)
			{
				Id_t post = p2.get(j);
				add_synapse(p1_index, post, WT(winit_dist(generator),wmin_dist(generator),wmax_dist(generator),ap_dist(generator),am_dist(generator)), ltp_dist(generator));
			}
			pre_syn_lookup[p1_index].back().set_end(synapses.size()-1);
		}
	}

	template<typename SYN, typename WT>
	inline
	void SimulationQueue<SYN,WT>::add_synapse(Id_t pre, Id_t post, WT w, Timeconst_t ltp)
	{
		synapses.push_back(SYN(pre,post,w,ltp));
		post_syn_lookup[post].push_back(synapses.size()-1);
		LOGGER("Adding pre_synaptic synapse # " << synapses.size()-1 << " from neuron " << pre << " to neuron " << post);
	}

	template<typename SYN, typename WT>
	void SimulationQueue<SYN,WT>::add_event(event * e)
	{
		eventQueue.push(e);
		LOGGER("Adding event of type " << e->get_type() << " for time " << e->time << " object " << e->get_linked_object_id());
	}

	template<typename SYN, typename WT>
	void SimulationQueue<SYN,WT>::run_until_empty()
	{
		while (!eventQueue.empty()) {
			run_one_event();
		}
	}

	template<typename SYN, typename WT>
	std::vector<Id_t> SimulationQueue<SYN,WT>::get_pre_synapse_ranges(Id_t const& neuron) const
	{
		return post_syn_lookup[neuron];
	}

	template<typename SYN, typename WT>
	std::vector<SynapseRange> SimulationQueue<SYN,WT>::get_synapse_ranges(Id_t const& neuron) const
	{
		return pre_syn_lookup[neuron];
	}

	template<typename SYN, typename WT>
	SYN* SimulationQueue<SYN,WT>::get_synapse_pointer(Id_t const& synapse)
	{
		return &(synapses[synapse]);
	}

	template<typename SYN, typename WT>
	SYN const* SimulationQueue<SYN,WT>::get_synapse_pointer(Id_t const& synapse) const
	{
		return &(synapses[synapse]);
	}


	template<typename SYN, typename WT>
	Neuron* SimulationQueue<SYN,WT>::get_neuron_pointer(Id_t const& nrn)
	{
		return &(neurons[nrn]);
	}

	template<typename SYN, typename WT>
	Time_t SimulationQueue<SYN,WT>::get_time() const
	{
		return time;
	}

	template<typename SYN, typename WT>
	std::vector<Spike_t>& SimulationQueue<SYN,WT>::get_spikes()
	{
		return spike_list;
	}

	template<typename SYN, typename WT>
	void SimulationQueue<SYN,WT>::add_spike(Time_t t, Id_t nrn)
	{
		spike_list.push_back(std::make_tuple(t,nrn));
	}

	template<typename SYN, typename WT>
	void SimulationQueue<SYN,WT>::print_spikes(std::string filename, Realtime_t scale)
	{
		std::ofstream file(filename,std::ios::out);
		for (auto pair : spike_list)
		{
			file << std::get<1>(pair) << "," << float(std::get<0>(pair))*scale << "\n";
		}
		file.close();
	}

	template<typename SYN, typename WT>
	void SimulationQueue<SYN,WT>::print_pre_weights(Id_t nrn, std::string filename) const
	{
		std::ofstream file(filename,std::ios::out);
		for (Id_t syn_id : get_pre_synapse_ranges(nrn))
		{
			SYN const* syn = get_synapse_pointer(syn_id);
			file << syn->get_weight().calc_current() << "\n";
		}
		file.close();

	}

	template<typename SYN, typename WT>
	void SimulationQueue<SYN,WT>::print_pre_weights(Population const& pop, std::string filename) const
	{
		for (unsigned int i=0; i<pop.size(); ++i)
		{
			Id_t nrn = pop.get(i);
			std::stringstream stst("");
			stst << filename << nrn;
			std::ofstream file(stst.str(),std::ios::out);
			for (Id_t syn_id : get_pre_synapse_ranges(nrn))
			{
				SYN const* syn = get_synapse_pointer(syn_id);
				file << syn->get_weight().calc_current() << "\n";
			}
			file.close();
		}
	}

	template<typename SYN, typename WT>
	std::vector<Spike_t> SimulationQueue<SYN,WT>::get_new_spikes()
	{
		if (last_spike_fetched < spike_list.size())
		{
			std::vector<Spike_t> ret(spike_list.begin()+last_spike_fetched, spike_list.end());
			last_spike_fetched = spike_list.size();
			return ret;
		}
		else return {};
	}

	template class SimulationQueue<RectSynapse,RectWeight>;
	template class SimulationQueue<ExpSynapse,ExpWeight>;
}
