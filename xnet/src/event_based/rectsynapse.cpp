#include "logger.h"
#include "event_based/rectsynapse.h"

namespace xnet
{
	RectSynapse::RectSynapse(std::size_t pre, std::size_t post, RectWeight const& w, Timeconst_t ltp, bool hard_inhibit) :
		Synapse(pre,post,w,ltp,hard_inhibit)
	{
	}

	Current_t RectSynapse::eval_pre_event(Time_t t)
	{
		last_pre_time = t;
		return get_current();
	}

	void RectSynapse::eval_post_event(Time_t t)
	{
		stdp(t);
	}

	void RectSynapse::stdp(Time_t t)
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

}
