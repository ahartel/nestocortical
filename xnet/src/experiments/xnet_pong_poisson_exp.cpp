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
#include "expsynapse.h"
#include "expweight.h"
#include "PongPoissonConnector.h"

using namespace std;


int main(int argc, char* argv[])
{
	int court_width = 16;
	int court_height = 16;
	int num_output_neurons = 16;
	int num_intermediate_neurons = 16;
	int num_dvs_addresses = court_height + court_width;
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

	xnet::SimulationQueue<xnet::ExpSynapse,xnet::ExpWeight> theSimulation;

	auto input = theSimulation.create_population_normal(
		num_dvs_addresses,
		// neuron parameters
		{1000.0,0.0},
		{50.0,0.0},
		{100,0},
		{15,0},
		{500.0,100.0} // delay
	);
	auto control = theSimulation.create_population_fixed(court_height,{1000.0,50.,100,15});
	//auto intermediate = theSimulation.create_population_fixed(
	//	num_intermediate_neurons,
	//	{3000.0,100.0,10,50} // neuron parameters
	//);
	auto output = theSimulation.create_population_fixed(num_output_neurons,{6000.0,100.0,50,200});

	theSimulation.connect_all_to_all_normal(input,output,
											{1.0,0.2}, //wmin
											{3000.0,600.0}, //wmax
											{300.0,60.0}, // winit
											{150.0,30.0}, // ap
											{150.0,30.0}, // am
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

	theSimulation.connect_one_to_one_identical(control, output,
		xnet::ExpWeight(6000.0,0.0,11000.0,0.0,0.0),15.0);

	//theSimulation.connect_all_to_all_wta(intermediate);
	theSimulation.connect_all_to_all_wta(output);

	theSimulation.print_pre_weights(output,filename_base+"/xnet_pong_weights_initial_");

	runPongPoissonConnector(theSimulation,pong,output,filename_base,num_repetitions);

	theSimulation.print_pre_weights(output,filename_base+"/xnet_pong_weights_final_");

}

//# vim: set noexpandtab

