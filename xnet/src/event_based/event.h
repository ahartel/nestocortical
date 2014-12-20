#pragma once
#include "xnet_types.h"

class event {
public:
	event (Time_t t) : time(t)
	{
	}

	virtual void processEvent () = 0;

	Time_t time;
};

struct eventComparator {
  bool operator() (const event * left, const event * right) const {
    return left->time > right->time;
  }
};

