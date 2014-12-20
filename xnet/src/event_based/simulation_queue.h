#pragma once
#include <queue>
#include "event_based/event.h"
#include "event_based/pre_syn_event.h"
#include "event_based/post_syn_event.h"
#include "event_based/psp_event.h"

class Simulation
{
public:
	Simulation () : time(0), eventQueue()
	{
	}
	void run();
	void scheduleEvent(event* newEvent)
	{
		eventQueue.push(newEvent);
	}
	Time_t time;
protected:
	std::priority_queue<event*, std::vector<event*, std::allocator<event*> >,
		eventComparator> eventQueue;
};
