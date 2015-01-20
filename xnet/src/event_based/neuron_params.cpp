#include "neuron_params.h"

namespace xnet
{
	Neuron_params::Neuron_params(
		Membrane_t th,
		Timeconst_t tm,
		Time_t tr,
		Time_t ti) :
		V_th(th),
		tau_mem(tm),
		Tref(tr),
		Tinhibit(ti),
		Tdelay(0)
	{
	}

	Neuron_params::Neuron_params(
		Membrane_t th,
		Timeconst_t tm,
		Time_t tr,
		Time_t ti,
		Time_t td) :
		Neuron_params(th,tm,tr,ti)
	{
		Tdelay = td;
	}
}
