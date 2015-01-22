#pragma once
#include <cstddef>
#include "event_based/range_type.h"

// Documentation last updated: 2015-01-08
// A Population holds a start and an end ID of a sequence of neurons

namespace xnet
{
	class Population : public RangeType
	{
	public:
		explicit Population();
		explicit Population(std::size_t s);
		explicit Population(std::size_t s, std::size_t e);
	private:
	};
}
