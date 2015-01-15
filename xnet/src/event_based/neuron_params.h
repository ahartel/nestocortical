#pragma once
#include "xnet_types.h"

namespace xnet
{
	struct Neuron_params
	{
		Neuron_params(
			Membrane_t th,
			Timeconst_t tm,
			Timeconst_t tr,
			Timeconst_t ti);
		Membrane_t V_th;
		Timeconst_t tau_mem;
		Timeconst_t tau_ref;
		Timeconst_t Tinhibit;
	};
}
