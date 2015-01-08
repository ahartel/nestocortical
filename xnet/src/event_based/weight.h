#pragma once
#include "xnet_types.h"

namespace xnet {
	class Weight
	{
	public:
		Weight(Weight_t w, float g) : weight(w), gmax(g) {};
	private:
		Weight_t weight;
		float gmax;
	};
}
