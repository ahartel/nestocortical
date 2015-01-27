#pragma once
#include <cstddef>
#include "synapse.h"
#include "expweight.h"

namespace xnet {
	class ExpSynapse : public Synapse<ExpWeight>
	{
	public:
		explicit ExpSynapse(std::size_t pre, std::size_t post, ExpWeight const& w, Timeconst_t ltp, bool hard_inhibit=false);
		virtual Current_t eval_pre_event(Time_t);
		virtual void eval_post_event(Time_t);
	private:

		Time_t last_post_time;
	};
}
