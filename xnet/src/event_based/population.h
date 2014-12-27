#pragma once
#include <cstddef>

class Population
{
public:
	Population(std::size_t s);
	void set_end(std::size_t end);
	std::size_t size() const;
private:
	std::size_t start,end;
};
