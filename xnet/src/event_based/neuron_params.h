#pragma once
#include "xnet_types.h"

namespace xnet
{
	struct Neuron_params
	{
		Neuron_params(Membrane_t th, Timeconst_t tm, Timeconst_t tr);
		Membrane_t V_th;
		Timeconst_t tau_mem;
		Timeconst_t tau_ref;
	};
}
