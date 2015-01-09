#pragma once
#include "xnet_types.h"

namespace xnet {
	class Weight
	{
	public:
		Weight();
		Weight(Weight_t w, float g);
		Current_t calc_current();
	private:
		Weight_t weight;
		Current_t gmax;
	};
}
