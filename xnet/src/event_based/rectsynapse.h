#pragma once
#include <cstddef>
#include "synapse.h"
#include "rectweight.h"

namespace xnet {
	class RectSynapse : public Synapse<RectWeight>
	{
	public:
		explicit RectSynapse(std::size_t pre, std::size_t post, RectWeight const& w, Timeconst_t ltp, bool hard_inhibit=false);
		virtual Current_t eval_pre_event(Time_t);
		virtual void eval_post_event(Time_t);
	private:
		void stdp(Time_t);
	};
}
