#pragma once
#include <cstddef>
#include "weight.h"

namespace xnet {
	class Synapse
	{
	public:
		Synapse(std::size_t pre, std::size_t post);
		void generate_psp_event();
	private:
		Weight _weight;
		Time_t _delay;
	};
}
