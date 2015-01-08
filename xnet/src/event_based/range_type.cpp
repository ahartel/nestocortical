#include <stdexcept>
#include "event_based/range_type.h"

RangeType::RangeType(std::size_t s) : start(s), end(-1)
{
}

RangeType::RangeType(std::size_t s, std::size_t e) : start(s), end(e)
{
}

RangeType::RangeType() : start(-1), end(-1)
{
}

void RangeType::set_start(std::size_t s)
{
	start = s;
}

void RangeType::set_end(std::size_t e)
{
	end = e;
}

std::size_t RangeType::size() const
{
	return end-start+1;
}

std::size_t RangeType::get(std::size_t pos) const
{
	if (start + pos > end)
		throw std::out_of_range("RangeType range exceeded");
	return start + pos;
}
