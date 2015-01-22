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
#include "pongpoisson.h"

using namespace std;

template<typename T>
size_t max(std::vector<T> const& input)
{
	T max_value = 0;
	std::size_t max_pos = 0;
	for (size_t i=0; i<input.size(); ++i)
	{
		if (input[i] > max_value)
		{
			max_value = input[i];
			max_pos = i;
		}
	}
	return max_pos;
}

int main(int argc, char* argv[])
{
	int court_width = 16;
	int court_height = 16;
	int num_output_neurons = 16;
	int num_intermediate_neurons = 16;
	int num_dvs_addresses = court_height + court_width;
	Time_t dt = 10;
	float timebase = 1.0e-4;
	int	num_repetitions = atoi(argv[1]);
	std::string filename_base(argv[2]);
	pos2D velocity = std::make_tuple(50.0,55.0); // pixels per second
	float ball_radius = 1.0;
	float paddle_width = 1.0;
	float paddle_speed = 1.0;

	//PongDVS pong {
	PongPoisson pong {
		court_width, court_height,
		velocity,
		ball_radius, paddle_width,
		filename_base+"/pong_record"
	};

	xnet::Simulation theSimulation;

	auto input = theSimulation.create_population_normal(
		num_dvs_addresses,
		{1000.0,0.0},
		{50.0,0.0},
		{100,0},
		{15,0},
		{50.0,30.0} // neuron parameters
	);
	auto control = theSimulation.create_population_fixed(court_height,{1000.0,50.,100,15});
	//auto intermediate = theSimulation.create_population_fixed(
	//	num_intermediate_neurons,
	//	{3000.0,100.0,10,50} // neuron parameters
	//);
	auto output = theSimulation.create_population_fixed(num_output_neurons,{4000.0,100.0,10,1000});

	//theSimulation.connect_all_to_all_normal(input,output0,
	//										{1.0,0.2}, //wmin
	//										{1000.0,200.0}, //wmax
	//										{800.0,160.0}, // winit
	//										{100.0,20.0}, // ap
	//										{50.0,10.0}, // am
	//										{30.0,0.0} // ltp
	//									);
	theSimulation.connect_all_to_all_normal(input,output,
											{1.0,0.2}, //wmin
											{1000.0,200.0}, //wmax
											{800.0,160.0}, // winit
											{100.0,20.0}, // ap
											{50.0,10.0}, // am
											{100.0,20.0} // ltp
										);
	//theSimulation.connect_all_to_all_normal(input,intermediate,
	//										{1.0,0.2}, //wmin
	//										{1000.0,200.0}, //wmax
	//										{800.0,160.0}, // winit
	//										{100.0,20.0}, // ap
	//										{50.0,10.0}, // am
	//										{50.0,0.0} // ltp
	//									);
	//theSimulation.connect_all_to_all_normal(intermediate,output,
	//										{1.0,0.2}, //wmin
	//										{1000.0,300.0}, //wmax
	//										{200.0,40.0}, // winit
	//										{100.0,20.0}, // ap
	//										{50.0,10.0}, // am
	//										{100.0,10.0} // ltp
	//									);

	//theSimulation.connect_one_to_one_identical(control, output,
	//	xnet::Weight(3000.0,0.0,11000.0,0.0,0.0),15.0);

	//theSimulation.connect_all_to_all_wta(intermediate);
	theSimulation.connect_all_to_all_wta(output);

	theSimulation.print_pre_weights(output,filename_base+"/xnet_pong_weights_initial_");

	// time is in seconds
	Time_t time = 0;

	// one repetition consists of letting the ball bounce back and forth once
	for (int rep=0; rep<num_repetitions; ++rep)
	{
		// this is how long it takes to bounce the ball back and forth once
		for (Time_t t=0; t<court_width/std::get<0>(velocity)*2*10000; t+=dt)
		{
			auto output_spikes = theSimulation.get_new_spikes();
			std::vector<int> guess(court_height);
			// collect the spikes of the output neurons and count them
			for (auto spike : output_spikes)
			{
				for (unsigned int n=output.begin(); n<output.end()+1;++n)
				{
					if (std::get<1>(spike) == output.get(n))
					{
						guess[output.get(n)] += 1;
					}
				}
			}
			// advance the pong simulation by 1 ms
			auto input_spikes = pong.advance(0.001,max(guess));
			// present the newly generated input data to the network
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

	theSimulation.print_pre_weights(output,filename_base+"/xnet_pong_weights_final_");

}

//# vim: set noexpandtab

