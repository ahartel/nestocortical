#include "weight.h"

namespace xnet
{
	Weight::Weight() : /*weight(255),*/ gmax(1000)
	{
	};
	Weight::Weight(float g) : gmax(g)
	{
	};
	Current_t Weight::calc_current() const
	{
		//return weight/wmax*gmax;
		return gmax;
	}
}
