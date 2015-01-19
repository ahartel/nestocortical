#include <map>
#include <cstdlib>
#include <vector>
#include <tuple>
#include <iostream>
#include <random>
#include <fstream>
#include "logger.h"
#include "simulation_queue.h"
#include "pongdvs.h"

using namespace std;

int main(int argc, char* argv[])
{
	int court_width = 16;
	int court_height = 16;
	int num_output_neurons = 2;
	int num_intermediate_neurons = 16;
	int num_dvs_addresses = court_height * 2;
	Time_t dt = 10;
	float timebase = 1.0e-4;
	int	num_repetitions = atoi(argv[1]);
	std::string filename_base(argv[2]);
	pos2D velocity = std::make_tuple(500.0,600.0); // pixels per second
	float ball_radius = 1.0;
	float paddle_width = 1.0;

	PongDVS pdvs {
		court_width, court_height,
		velocity,
		ball_radius, paddle_width,
		filename_base+"/pong_record"
	};

	xnet::Simulation theSimulation;

	auto input = theSimulation.create_population_fixed(num_dvs_addresses,{1000.0,50.,100,15});
	auto control0 = theSimulation.create_population_fixed(1,{1000.0,50.,100,15});
	auto control1 = theSimulation.create_population_fixed(1,{1000.0,50.,100,15});
	auto output0 = theSimulation.create_population_fixed(1,{5000.0,50.0,100,15});
	auto output1 = theSimulation.create_population_fixed(1,{5000.0,50.0,100,15});
	auto intermediate = theSimulation.create_population_fixed(num_intermediate_neurons,{5000.0,50.0,100,15});

	std::default_random_engine generator;

	//theSimulation.connect_all_to_all_normal(input,output0,
	//										{1.0,0.2}, //wmin
	//										{1000.0,200.0}, //wmax
	//										{800.0,160.0}, // winit
	//										{100.0,20.0}, // ap
	//										{50.0,10.0}, // am
	//										{30.0,0.0} // ltp
	//									);
	//theSimulation.connect_all_to_all_normal(input,output1,
	//										{1.0,0.2}, //wmin
	//										{1000.0,200.0}, //wmax
	//										{800.0,160.0}, // winit
	//										{100.0,20.0}, // ap
	//										{50.0,10.0}, // am
	//										{30.0,0.0} // ltp
	//									);
	theSimulation.connect_all_to_all_normal(intermediate,output0,
											{1.0,0.2}, //wmin
											{1000.0,200.0}, //wmax
											{800.0,160.0}, // winit
											{100.0,20.0}, // ap
											{50.0,10.0}, // am
											{30.0,0.0} // ltp
										);
	theSimulation.connect_all_to_all_normal(intermediate,output1,
											{1.0,0.2}, //wmin
											{1000.0,200.0}, //wmax
											{800.0,160.0}, // winit
											{100.0,20.0}, // ap
											{50.0,10.0}, // am
											{30.0,0.0} // ltp
										);
	theSimulation.connect_all_to_all_normal(input,intermediate,
											{1.0,0.2}, //wmin
											{1000.0,200.0}, //wmax
											{800.0,160.0}, // winit
											{100.0,20.0}, // ap
											{50.0,10.0}, // am
											{30.0,0.0} // ltp
										);
	theSimulation.connect_all_to_all_identical(control0,output0,{5000.0,0.0,11000.0,0.0,0.0},15.0);
	theSimulation.connect_all_to_all_identical(control1,output1,{5000.0,0.0,11000.0,0.0,0.0},15.0);

	theSimulation.connect_all_to_all_wta(intermediate);

	theSimulation.print_pre_weights(output0,filename_base+"/xnet_pong_weights_initial_");

	// time is in seconds
	Time_t time = 0;

	int angles[8] = {0,45,90,135,180,225,270,315};
	std::uniform_int_distribution<int> angle_dist(0,7);

	for (int rep=0; rep<num_repetitions; ++rep)
	{
		for (Time_t t=0; t<court_width/std::get<0>(velocity)*2*10000; t+=dt)
		{
			auto output_spikes = theSimulation.get_new_spikes();
			unsigned int up(0),down(0);
			for (auto spike : output_spikes)
			{
				LOGGER("spike: " << std::get<0>(spike) << "," << std::get<1>(spike));
				if (std::get<1>(spike) == num_dvs_addresses+2)
				{
					LOGGER("Found up spike");
					up += 1;
				}
				else if (std::get<1>(spike) == num_dvs_addresses + 3)
				{
					LOGGER("Found down spike");
					down += 1;
				}
			}
			auto input_spikes = pdvs.advance(0.001,up,down);

			for (auto spike : input_spikes)
			{
				theSimulation.add_event(new xnet::pre_syn_event(time,std::get<1>(spike)));
			}
			time += dt;
			theSimulation.run_until_empty();
		}
	}

	LOGGER(theSimulation.get_spikes().size());

	theSimulation.print_spikes(filename_base+"/xnet_pong_spikes.dat",timebase);

	theSimulation.print_pre_weights(output0,filename_base+"/xnet_pong_weights_final_");

}
//# vim: set noexpandtab
