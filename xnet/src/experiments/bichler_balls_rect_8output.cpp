#include <map>
#include <cstdlib>
#include <vector>
#include <tuple>
#include <iostream>
#include <random>
#include <fstream>
#include "logger.h"
#include "simulation_queue.h"
#include "DVS.h"
#include "BallCamera.h"
#include "BallConnector.h"

using namespace std;

/*
   for this experiment a time unit is 10^-4 seconds
*/

int main(int argc, char* argv[])
{
	int image_width = 16;
	int image_height = 16;
	int num_neurons = 8;
	int num_dvs_addresses = 2 * image_width * image_height;
	int	num_repetitions = atoi(argv[1]);
	std::string filename_base = std::string(argv[2])+"/bichler_balls_8neurons";
	float velocity = 480.0;
	float ball_radius = 6.0;

	DVS dvs(image_width,image_height);
	BallCamera cam {
            0.0, // angle in degrees
            velocity,
            ball_radius,
            image_width,
            image_height
	};

	xnet::Simulation theSimulation;

	auto pop1 = theSimulation.create_population_fixed(num_dvs_addresses,{1000.0,50.0,100,15});
	auto pop2 = theSimulation.create_population_fixed(num_neurons,{10000.0,50.0,100,15});


	theSimulation.connect_all_to_all_normal(pop1,pop2,
											{1.0,0.2}, //wmin
											{1000.0,200.0}, //wmax
											{800.0,160.0}, // winit
											{100.0,20.0}, // ap
											{50.0,10.0}, // am
											{15.0,0.0} // ltp
										);

	theSimulation.connect_all_to_all_wta(pop2);

	theSimulation.print_pre_weights(pop2,filename_base+"_weights_initial_");

	runBallConnector(theSimulation,cam,dvs,filename_base,num_repetitions);

	theSimulation.print_pre_weights(pop2,filename_base+"_weights_final_");

}
//# vim: set noexpandtab
