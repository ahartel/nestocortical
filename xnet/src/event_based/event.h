#pragma once
#include "xnet_types.h"

namespace xnet
{
	enum EventType {SIL, PST, PRE, PSP};

	class event {
	public:
		event (Time_t ti, EventType ty, Id_t lo) :
			time(ti),
			linked_object(lo),
			type(ty)
		{
		}

		//virtual void processEvent () = 0;

		EventType get_type() const {return type;}
		Id_t get_linked_object_id() const {return linked_object;}

		Time_t time;
	private:
		Id_t linked_object;
		EventType type;
	};

	struct eventComparator {
	  bool operator() (const event * left, const event * right) const {
		if (left->time == right->time)
			return left->get_type() > right->get_type();
		else
			return left->time > right->time;
	  }
	};
}
