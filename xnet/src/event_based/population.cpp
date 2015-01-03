#include <stdexcept>
#include "event_based/population.h"

Population::Population(std::size_t s) : start(s), end(-1)
{
}

void Population::set_end(std::size_t e)
{
	end = e;
}

std::size_t Population::size() const
{
	return end-start+1;
}

std::size_t Population::get(std::size_t pos) const
{
	if (start + pos > end)
		throw std::out_of_range("Population range exceeded");
	return start + pos;
}
