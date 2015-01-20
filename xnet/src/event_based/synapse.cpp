#include "logger.h"
#include "event_based/synapse.h"

namespace xnet
{
	//template <class WT>
	Synapse::Synapse(std::size_t pre, std::size_t post, Weight const& w, Timeconst_t ltp, bool hard_inhibit) :
		pre_neuron(pre),
		post_neuron(post),
		_weight(w),
		hard(hard_inhibit),
		last_pre_time(-1),
		T_ltp(ltp)
	{
	}

	Current_t Synapse::eval_pre_event(Time_t t)
	{
		last_pre_time = t;
		return get_current();
	}

	void Synapse::stdp(Time_t t)
	{
		// update
		if (last_pre_time >= 0 && t-last_pre_time <= T_ltp)
		{
			_weight.update_pos();
			LOGGER("Facilitating");
		}
		else
		{
			_weight.update_neg();
			LOGGER("Depressing");
		}
	}

	Id_t Synapse::get_post_neuron() const
	{
		return post_neuron;
	}

	inline
	Current_t Synapse::get_current() const
	{
		return _weight.calc_current();
	}

	bool Synapse::hard_inhibit() const
	{
		return hard;
	}

	Weight Synapse::get_weight() const
	{
		return _weight;
	}
}
