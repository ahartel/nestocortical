#pragma once
#include <cstddef>

namespace xnet
{
	class RangeType
	{
	public:
		explicit RangeType();
		explicit RangeType(std::size_t s);
		explicit RangeType(std::size_t s, std::size_t e);
		void set_start(std::size_t s);
		void set_end(std::size_t e);
		std::size_t size() const;
		std::size_t get(std::size_t pos) const;
		std::size_t begin() const;
		std::size_t end() const;
		bool non_empty() const;
	protected:
		void update_size();
		int _start, _end;
		int _size;
	};
}
