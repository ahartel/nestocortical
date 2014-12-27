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
