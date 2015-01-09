#pragma once
#include <cstddef>

namespace xnet
{
	class RangeType
	{
	public:
		RangeType();
		RangeType(std::size_t s);
		RangeType(std::size_t s, std::size_t e);
		void set_start(std::size_t s);
		void set_end(std::size_t e);
		std::size_t size() const;
		std::size_t get(std::size_t pos) const;
		std::size_t begin() const;
		std::size_t end() const;
	protected:
		void update_size();
		std::size_t _start, _end, _size;
	};
}
