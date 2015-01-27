#include "logger.h"
#include "event_based/expsynapse.h"

namespace xnet
{
	ExpSynapse::ExpSynapse(std::size_t pre, std::size_t post, ExpWeight const& w, Timeconst_t ltp, bool hard_inhibit) :
		Synapse(pre,post,w,ltp,hard_inhibit),
		last_post_time(-1)
	{
	}

	Current_t ExpSynapse::eval_pre_event(Time_t t)
	{
		last_pre_time = t;
		if (last_post_time >= 0)
		{
			_weight.update_neg(t-last_post_time,T_ltp);
			LOGGER("Depressing");
		}

		return get_current();
	}

	void ExpSynapse::eval_post_event(Time_t t)
	{
		last_post_time = t;
		if (last_pre_time >= 0)
		{
			_weight.update_pos(t-last_pre_time,T_ltp);
			LOGGER("Facilitating");
		}
	}

}
