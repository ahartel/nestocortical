#include "event_based/simulation_queue.h"

void Simulation::run() {
	while (!eventQueue.empty()) {
		event * nextEvent = eventQueue.top();
		eventQueue.pop();
		time = nextEvent->time;
		nextEvent->processEvent();
		delete nextEvent;
	}
}
