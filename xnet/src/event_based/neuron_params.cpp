#include "neuron_params.h"

namespace xnet
{
	Neuron_params::Neuron_params(Membrane_t th, Timeconst_t tm) :
		V_th(th),
		tau_m(tm)
	{
	}
}
