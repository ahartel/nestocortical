#pragma once
#include <queue>
#include "event_based/population.h"
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
	Population create_population(std::size_t s);
	void connect_all_to_all(Population& p1, Population& p2);
	void add_events(std::vector<event *>&);
	void run_until_empty();
protected:
	Time_t time;
	std::priority_queue<event*, std::vector<event*, std::allocator<event*> >,
		eventComparator> eventQueue;
};
