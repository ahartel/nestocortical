#include "neuron_params.h"

namespace xnet
{
	Neuron_params::Neuron_params(
		Membrane_t th,
		Timeconst_t tm,
		Timeconst_t tr,
		Timeconst_t ti) :
		V_th(th),
		tau_mem(tm),
		tau_ref(tr),
		Tinhibit(ti)
	{
	}
}
