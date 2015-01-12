#include <stdexcept>
#include "logger.h"
#include "event_based/range_type.h"

namespace xnet
{
	RangeType::RangeType(std::size_t s) : _start(s), _end(-1), _size(-1)
	{
	}

	RangeType::RangeType(std::size_t s, std::size_t e) : _start(s), _end(e+1), _size(-1)
	{
		update_size();
	}

	RangeType::RangeType() : _start(-1), _end(-1), _size(-1)
	{
	}

	void RangeType::update_size()
	{
		_size = _end-_start;
	}

	void RangeType::set_start(std::size_t s)
	{
		_start = s;
		update_size();
	}

	void RangeType::set_end(std::size_t e)
	{
		_end = e+1;
		update_size();
	}

	std::size_t RangeType::size() const
	{
		if (_size < 0)
			throw std::out_of_range("Start or End in RangeType not fully defined.");
		return _size;
	}

	std::size_t RangeType::get(std::size_t pos) const
	{

		if (_size < 0)
			throw std::out_of_range("Start or End in RangeType not fully defined.");
		if (_start + pos >= _end)
			throw std::out_of_range("RangeType range exceeded");

		return _start + pos;
	}

	std::size_t RangeType::begin() const
	{
		return _start;
	}

	std::size_t RangeType::end() const
	{
		return _end;
	}

	bool RangeType::non_empty() const
	{
		return (_start >= 0) && (_end >= 0) && (_end >= _start);
	}
}
