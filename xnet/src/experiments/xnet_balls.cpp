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
	float dt = 1.0;
	int	num_repetitions = atoi(argv[1]);
	float velocity = 0.48;
	float ball_radius = 6.0;

	DVS dvs(image_width,image_height);
	BallCamera cam {
            3.1416/4.,
            velocity,
            ball_radius,
            image_width,
            image_height
	};

	xnet::Simulation theSimulation;

	auto pop1 = theSimulation.create_population_fixed(num_dvs_addresses,{1000.0,5.0,10.0});
	auto pop2 = theSimulation.create_population_fixed(num_neurons,{40000.0,5.0,10.0});

	std::default_random_engine generator;
	std::normal_distribution<float> weight_distribution(800.0,160.0);
	std::normal_distribution<float> am_distribution(100.0,20.0);
	std::normal_distribution<float> ap_distribution(50.0,10.0);
	std::normal_distribution<float> wmin_distribution(1.0,0.2);
	std::normal_distribution<float> wmax_distribution(1000.0,200.0);

	theSimulation.connect_all_to_all_normal(pop1,pop2,
											{1.0,0.2}, //wmin
											{1000.0,200.0}, //wmax
											{800.0,160.0}, // winit
											{100.0,20.0}, // ap
											{50.0,10.0} // am
										);

	//dump_weights(synapses, "./results/xnet_balls_weights_initial.txt", num_neurons, num_dvs_addresses);

	float time = 0;
	int angles[8] = {0,45,90,135,180,225,270,315};
	std::uniform_int_distribution<int> angle_dist(0,7);
	for (int rep=0; rep<num_repetitions; ++rep)
	{
		cout << "rep " << rep << endl;
		//for (float angle=0; angle<360; angle+=45)
		//{
		int angle = angles[angle_dist(generator)];
			cout << "-------- time = " << time << ", angle = " << angle << " ----------" << endl;
			//cout << "angle " << angle << endl;
			cam.reset_and_angle(angle,time);
			for (float t=0.0; t<100.0; t+=dt)
			{
				int on_pixels = 0;
				int off_pixels = 0;
				auto image = cam.generate_image(time);
				//for (auto row : image)
				//{
				//	cout << row.size() << endl;
				//	for (auto col : row)
				//	{
				//		cout << col << endl;
				//	}
				//}

				auto image_diff = dvs.calculate_spikes(image);
				for (int row=0; row<image_height; ++row)
				{
					for (int col=0; col<image_width; ++col)
					{
						if (image_diff[row][col] > 0)
						{
							on_pixels += 1;

							theSimulation.add_event(new xnet::pre_syn_event(time,(row*image_width+col)*2));
							//for (int j=0; j<num_neurons; ++j)//Synapse synapse : synapses[pixel])
								//synapses[(row*image_width+col)*2][j].pre(time);
						}
						else if (image_diff[col][row] < 0)
						{
							off_pixels += 1;

							theSimulation.add_event(new xnet::pre_syn_event(time,(row*image_width+col)*2+1));
							//for (int j=0; j<num_neurons; ++j)//Synapse synapse : synapses[pixel])
								//synapses[(row*image_width+col)*2+1][j].pre(time);
						}
					}
				}
				//if (on_pixels > 0 || off_pixels > 0)
				//{
				//	cout << "ON: " << on_pixels << ", OFF: " << off_pixels << endl;
				//}
				time += dt;
			}
			// add a time-step of 100 ms between each run
			time += 100.0;
		//}
	}

	LOGGER(theSimulation.get_spikes().size());
	//theSimulation.run(10);
	theSimulation.run_until_empty();

	theSimulation.print_spikes("./results/xnet_balls_spikes.dat");

	//dump_weights(synapses, "./results/xnet_balls_weights_final.txt", num_neurons, num_dvs_addresses);

}
//# vim: set noexpandtab
