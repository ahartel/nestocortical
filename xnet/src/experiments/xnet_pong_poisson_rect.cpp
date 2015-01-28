#include <map>
#include <cstdlib>
#include <vector>
#include <tuple>
#include <iostream>
#include <random>
#include <fstream>
#include <algorithm>
#include "logger.h"
#include "simulation_queue.h"
#include "pongdvs.h"
#include "pongpoisson.h"
#include "rectsynapse.h"
#include "rectweight.h"
#include "PongPoissonConnector.h"

using namespace std;


int main(int argc, char* argv[])
{
	if (argc != 3)
		throw std::invalid_argument("Please give number of repetitions and filename base path as arguments");

	unsigned int court_width = 16;
	unsigned int court_height = 16;
	int num_output_neurons = 16;
	int num_intermediate_neurons = 32;
	int num_dvs_addresses = court_height*court_width;
	int	num_repetitions = atoi(argv[1]);
	std::string filename_base(argv[2]);
	pos2D velocity = std::make_tuple(50.0,55.0); // pixels per second
	float ball_radius = 1.0;
	float paddle_width = 1.0;

	xnet::SimulationQueue<xnet::RectSynapse,xnet::RectWeight> theSimulation;

	auto input = theSimulation.create_population_normal(
		num_dvs_addresses,
		// neuron parameters
		{1000.0,0.0},
		{50.0,0.0},
		{100,0},
		{15,0},
		{0.0,0.0} // delay
	);
	auto control = theSimulation.create_population_fixed(court_height,{1000.0,50.,100,15});
	auto intermediate = theSimulation.create_population_fixed(
		num_intermediate_neurons,
		{5000.0,100.0,100,500} // neuron parameters
	);
	auto output = theSimulation.create_population_fixed(num_output_neurons,{2000.0,100.0,40,500});

	theSimulation.connect_all_to_all_normal(input,intermediate,
											{1.0,0.2}, //wmin
											{2000.0,400.0}, //wmax
											{500.0,100.0}, // winit
											{100.0,20.0}, // ap
											{50.0,10.0}, // am
											{400.0,80.0} // ltp
										);
	//theSimulation.connect_all_to_all_normal(input,intermediate,
	//										{1.0,0.2}, //wmin
	//										{1000.0,200.0}, //wmax
	//										{800.0,160.0}, // winit
	//										{100.0,20.0}, // ap
	//										{50.0,10.0}, // am
	//										{50.0,0.0} // ltp
	//									);
	theSimulation.connect_all_to_all_normal(intermediate,output,
											{1.0,0.2}, //wmin
											{4000.0,800.0}, //wmax
											{1000.0,200.0}, // winit
											{200.0,40.0}, // ap
											{100.0,20.0}, // am
											{1000.0,200.0} // ltp
										);

	theSimulation.connect_one_to_one_identical(control, output,
		xnet::RectWeight(2000.0,0.0,11000.0,0.0,0.0),15.0);

	theSimulation.connect_all_to_all_wta(intermediate);
	theSimulation.connect_all_to_all_wta(output);

	theSimulation.print_pre_weights(intermediate,filename_base+"/xnet_pong_weights_initial_");
	theSimulation.print_pre_weights(output,filename_base+"/xnet_pong_weights_initial_");

	//PongDVS pong {
	PongPoisson pong {
		court_width, court_height,
		velocity,
		ball_radius, paddle_width,
		filename_base+"/pong_record",
		input,
		control
	};

	runPongPoissonConnector(theSimulation,pong,output,filename_base,num_repetitions);

	theSimulation.print_pre_weights(intermediate,filename_base+"/xnet_pong_weights_final_");
	theSimulation.print_pre_weights(output,filename_base+"/xnet_pong_weights_final_");

}

//# vim: set noexpandtab

