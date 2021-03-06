#pragma once
#include "xnet_types.h"

namespace xnet
{
	struct Neuron_params
	{
		Neuron_params(
			Membrane_t th,
			Timeconst_t tm,
			Time_t tr,
			Time_t ti);

		Neuron_params(
			Membrane_t th,
			Timeconst_t tm,
			Time_t tr,
			Time_t ti,
			Time_t td);

		Membrane_t V_th;
		Timeconst_t tau_mem;
		Time_t Tref;
		Time_t Tinhibit;
		Time_t Tdelay;
	};
}
