#pragma once
#include <cstddef>

class Population
{
public:
	Population(std::size_t s);
	void set_end(std::size_t end);
	std::size_t size() const;
	std::size_t get(std::size_t pos) const;
private:
	std::size_t start,end;
};
