#pragma once
#include <cstddef>
#include "weight.h"
#include "psp_event.h"

namespace xnet {
	//template <class WT>
	class Synapse
	{
	public:
		explicit Synapse(std::size_t pre, std::size_t post, Weight const& w, Timeconst_t ltp, bool hard_inhibit=false);
		Id_t get_post_neuron() const;
		Current_t eval_pre_event(Time_t t);
		bool hard_inhibit() const;
		void stdp(Time_t);
		Weight get_weight() const;
	private:
		Current_t get_current() const;

		Timeconst_t T_ltp;
		Id_t pre_neuron, post_neuron;
		Time_t last_pre_time;
		Weight _weight;
		Time_t _delay;
		bool hard;
	};
}
