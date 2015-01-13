#pragma once
#include <cmath>
#include "xnet_types.h"

namespace xnet {
	class Weight
	{
	public:
		Weight();
		Weight(float g);
		Current_t calc_current() const;
	private:
		//static const Weight_t wmax = std::pow(2,sizeof(Weight_t))-1;
		//Weight_t weight;
		Current_t gmax;
	};
}
