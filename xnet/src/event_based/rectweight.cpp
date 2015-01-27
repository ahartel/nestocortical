#include "rectweight.h"
#include <math.h>

namespace xnet
{
	RectWeight::RectWeight() :
		Weight()
	{
	}

	RectWeight::RectWeight(Current_t wgt, Current_t wmi, Current_t wma, Current_t apl, Current_t ami) :
		Weight(wgt,wmi,wma,apl,ami)
	{
	};

	void RectWeight::update_pos()
	{
		if (w >= 0)
		{
			w += ap;
			if (w > wmax)
			{
				w = wmax;
			}
		}
	}

	void RectWeight::update_neg()
	{
		if (w >= 0)
		{
			w -= am;
			if (w < wmin)
			{
				w = wmin;
			}
		}
	}
}
