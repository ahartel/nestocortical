#pragma once
#include "xnet_types.h"

namespace xnet
{
	enum class EventType {PRE, PSP, PST, SIL};

	class event {
	public:
		event (Time_t ti, EventType ty, Id_t lo) :
			time(ti),
			type(ty),
			linked_object(lo)
		{
		}

		//virtual void processEvent () = 0;

		Time_t time;
		EventType get_type() const {return type;}
		Id_t get_linked_object_id() const {return linked_object;}

	private:
		Id_t linked_object;
		EventType type;
	};

	struct eventComparator {
	  bool operator() (const event * left, const event * right) const {
		return left->time > right->time;
	  }
	};
}
