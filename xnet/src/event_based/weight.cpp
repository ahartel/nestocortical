#include "weight.h"
#include <math.h>

namespace xnet
{
	Weight::Weight() :
		w(0),
		wmin(0),
		wmax(0),
		ap(0),
		am(0)
	{
	}

	Weight::Weight(Current_t wgt, Current_t wmi, Current_t wma, Current_t apl, Current_t ami) :
		w(wgt),
		wmin(wmi),
		wmax(wma),
		ap(apl),
		am(ami)
	{
	};

	Current_t Weight::calc_current() const
	{
		//return weight/wmax*gmax;
		return w;
	}

	void Weight::update_pos()
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

	void Weight::update_neg()
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
