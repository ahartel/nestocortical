#include <vector>
#include "simulation_queue.h"

using namespace xnet;

int main()
{
	Simulation sim;
	auto pop1 = sim.create_population(1);
	auto pop2 = sim.create_population(1);
	sim.connect_all_to_all(pop1,pop2);

	sim.add_event(new psp_event(0,0));
	sim.run_until_empty();
}
