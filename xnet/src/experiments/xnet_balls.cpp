#include <map>
#include <cstdlib>
#include <vector>
#include <tuple>
#include <iostream>
#include <random>

#include "logger.h"
#include "simulation_queue.h"
#include "DVS.h"
#include "BallCamera.h"

using namespace std;

int main(int argc, char* argv[])
{
	int image_width = 16;
	int image_height = 16;
	int num_neurons = 48;
	int num_dvs_addresses = 2 * image_width * image_height;
	float dt = 1.0e-3;
	int	num_repetitions = atoi(argv[1]);
	std::string filename_base(argv[2]);
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

	auto pop1 = theSimulation.create_population_fixed(num_dvs_addresses,{1000.0,0.005,0.010,0.0015});
	auto pop2 = theSimulation.create_population_fixed(num_neurons,{40000.0,0.005,0.010,0.0015});

	std::default_random_engine generator;

	theSimulation.connect_all_to_all_normal(pop1,pop2,
											{1.0,0.2}, //wmin
											{1000.0,200.0}, //wmax
											{800.0,160.0}, // winit
											{100.0,20.0}, // ap
											{50.0,10.0} // am
										);

	theSimulation.connect_all_to_all_wta(pop2);

	theSimulation.print_pre_weights(pop2,filename_base+"/xnet_balls_weights_initial_");

	// time is in seconds
	Time_t time = 0;

	int angles[8] = {0,45,90,135,180,225,270,315};
	std::uniform_int_distribution<int> angle_dist(0,7);

	for (int rep=0; rep<num_repetitions; ++rep)
	{
		int angle = angles[rep%8];//angle_dist(generator)];
		cout << "-------- repetition = " << rep << ", time = " << time <<
			", angle = " << angle << " ----------" << endl;

		cam.reset_and_angle(angle,time);

		for (float t=0.0; t<0.100; t+=dt)
		{
			auto image = cam.generate_image(time);

			auto spikes = dvs.calculate_spikes(image);
			for (auto spike : spikes)
			{
				theSimulation.add_event(new xnet::pre_syn_event(time,spike));
			}
			time += dt;
		}
		// add a time-step of 100 ms between each run
		time += 0.100;
	}

	LOGGER(theSimulation.get_spikes().size());
	//theSimulation.run(10000);
	theSimulation.run_until_empty();

	theSimulation.print_spikes(filename_base+"/xnet_balls_spikes.dat");

	theSimulation.print_pre_weights(pop2,filename_base+"/xnet_balls_weights_final_");

}
//# vim: set noexpandtab
