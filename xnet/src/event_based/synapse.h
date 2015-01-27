#pragma once
#include <cstddef>
#include "xnet_types.h"

namespace xnet {
	template <class WT>
	class Synapse
	{
	public:
		explicit Synapse(
			std::size_t pre,
			std::size_t post,
			WT const& w,
			Timeconst_t ltp,
			bool hard_inhibit=false
		);
		Id_t get_post_neuron() const;
		bool hard_inhibit() const;
		virtual Current_t eval_pre_event(Time_t t) = 0;
		virtual void eval_post_event(Time_t) = 0;
		WT get_weight() const;
	protected:
		Current_t get_current() const;

		Timeconst_t T_ltp;
		Id_t pre_neuron, post_neuron;
		Time_t last_pre_time;
		WT _weight;
		bool hard;
	};
}
