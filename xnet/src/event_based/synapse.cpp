#include "logger.h"
#include "event_based/rectweight.h"
#include "event_based/expweight.h"
#include "event_based/synapse.h"

namespace xnet
{
	template<class WT>
	Synapse<WT>::Synapse(std::size_t pre, std::size_t post, WT const& w, Timeconst_t ltp, bool hard_inhibit) :
		pre_neuron(pre),
		post_neuron(post),
		_weight(w),
		hard(hard_inhibit),
		last_pre_time(-1),
		T_ltp(ltp)
	{
	}

	template <class WT>
	Id_t Synapse<WT>::get_post_neuron() const
	{
		return post_neuron;
	}

	template <class WT>
	inline
	Current_t Synapse<WT>::get_current() const
	{
		return _weight.calc_current();
	}

	template <class WT>
	bool Synapse<WT>::hard_inhibit() const
	{
		return hard;
	}

	template <class WT>
	WT Synapse<WT>::get_weight() const
	{
		return _weight;
	}

	template class Synapse<RectWeight>;
	template class Synapse<ExpWeight>;
}
