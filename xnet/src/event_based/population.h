#pragma once
#include <cstddef>
#include "event_based/range_type.h"

// Documentation last updated: 2015-01-08
// A Population holds a start and an end ID of a sequence of neurons

class Population : public RangeType
{
public:
	Population();
	Population(std::size_t s);
private:
};
