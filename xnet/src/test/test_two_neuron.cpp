#include <vector>
#include "logger.h"
#include "simulation_queue.h"

using namespace xnet;

int main()
{
	extern Simulation theSimulation;

	auto pop1 = theSimulation.create_population(1);
	auto pop2 = theSimulation.create_population(2);
	theSimulation.connect_all_to_all_identical(pop1,pop2,{128,1.0});

	theSimulation.add_event(new pre_syn_event(0,0));
	theSimulation.run_until_empty();
}
