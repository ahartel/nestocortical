#include "event_based/population.h"

namespace xnet
{
	Population::Population() : RangeType()
	{
	}

	Population::Population(std::size_t s) : RangeType(s)
	{
	}

	Population::Population(std::size_t s, std::size_t e) : RangeType(s,e)
	{
	}
}
