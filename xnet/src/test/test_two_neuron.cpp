#include <vector>
#include "simulation_queue.h"

int main()
{
	Simulation sim;
	auto pop1 = sim.create_population(1);
	auto pop2 = sim.create_population(1);
	sim.connect_all_to_all(pop1,pop2);

	std::vector<event*> events;
	events.push_back(new psp_event(0,0));
	sim.add_events(events);
	sim.run_until_empty();
}
