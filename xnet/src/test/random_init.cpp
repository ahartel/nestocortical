#include <vector>
#include <gtest/gtest.h>
#include <tuple>
#include "logger.h"
#include "simulation_queue.h"

using namespace xnet;

TEST(SIM,RANDOM_INIT)
{
	Simulation theSimulation;

	auto pop1 = theSimulation.create_population_uniform(
		1,
		{0.0,1000.0},
		{1.0,5.0},
		{1.0,2.0},
		{0.001,0.0002},
		{0.0,0.0}
	);
	auto pop2 = theSimulation.create_population_normal(
		2,
		{1000.0,200.0},
		{3.0,1.0},
		{1.0,0.2},
		{0.001,0.0002},
		{0.0,0.0}
	);
	theSimulation.connect_all_to_all_identical(pop1,pop2,RectWeight(1.0,1.0,10.0,1.0,1.0),15.0);

	theSimulation.add_event(new pre_syn_event(0,0));
	theSimulation.run_until_empty();
	std::vector<Spike_t> spikes = theSimulation.get_spikes();

	ASSERT_EQ(spikes.size(),3);
	EXPECT_EQ(std::get<0>(spikes[0]),0);
	EXPECT_EQ(std::get<1>(spikes[0]),0);
	EXPECT_EQ(std::get<0>(spikes[1]),0);
	EXPECT_EQ(std::get<1>(spikes[1]),1);
	EXPECT_EQ(std::get<0>(spikes[2]),0);
	EXPECT_EQ(std::get<1>(spikes[2]),2);
}

int main(int argc, char** argv) {
	::testing::InitGoogleTest(&argc, argv);
	::testing::FLAGS_gtest_death_test_style = "fast";
	return RUN_ALL_TESTS();
}
