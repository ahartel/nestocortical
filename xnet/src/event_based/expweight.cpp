#include "expweight.h"
#include <math.h>

namespace xnet
{
	ExpWeight::ExpWeight() :
		Weight()
	{
	}

	ExpWeight::ExpWeight(Current_t wgt, Current_t wmi, Current_t wma, Current_t apl, Current_t ami) :
		Weight(wgt,wmi,wma,apl,ami)
	{
	};

	void ExpWeight::update_pos(Time_t dt, Timeconst_t tau)
	{
		// only update excitatory weights
		if (w >= 0)
		{
			w += ap*std::exp(-dt/tau);
			if (w > wmax)
			{
				w = wmax;
			}
		}
	}

	void ExpWeight::update_neg(Time_t dt, Timeconst_t tau)
	{
		if (w >= 0)
		{
			w -= am*std::exp(-dt/tau);
			if (w < wmin)
			{
				w = wmin;
			}
		}
	}
}
