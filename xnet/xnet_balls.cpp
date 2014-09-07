#include <map>
#include <cstdlib>
#include <vector>
#include <tuple>
#include <iostream>
#include <fstream>
#include <random>
#include "xnet_types.h"

#include "neuron.h"
#define DEBUG_OUTPUT
#include "synapse.h"
#include "DVS.h"
#include "BallCamera.h"

using namespace std;
using namespace xnet;


int main(int argc, char* argv[])
{
	int image_width = 16;
	int image_height = 16;
	int num_neurons = 48;
	int num_dvs_addresses = 2 * image_width * image_height;
	float dt = 1.0;
	int	num_repetitions = atoi(argv[1]);

	DVS dvs(image_width,image_height);
	BallCamera cam {
            3.1416/4.,
            0.48,
            6.0,
            image_width,
            image_height
	};

	Neurons neurons(num_neurons, num_dvs_addresses);

	std::default_random_engine generator;
	std::normal_distribution<float> weight_distribution(800.0,160.0);
	std::normal_distribution<float> am_distribution(100.0,20.0);
	std::normal_distribution<float> ap_distribution(50.0,10.0);
	std::normal_distribution<float> wmin_distribution(1.0,0.2);
	std::normal_distribution<float> wmax_distribution(1000.0,200.0);

	SynapseArray synapses;
	synapses = new Synapse*[num_dvs_addresses];
	//vector<vector<Synapse>> synapses;
	for (int i=0; i<num_dvs_addresses; ++i)
	{
		synapses[i] = new Synapse[num_neurons];

		for (int j=0; j<num_neurons; ++j)
			synapses[i][j].set_parameters(
						i*num_dvs_addresses+j,&neurons,j,
						weight_distribution(generator),
						am_distribution(generator),
						ap_distribution(generator),
						wmin_distribution(generator),
						wmax_distribution(generator)
					);
	}

	dump_weights(synapses, "./results/xnet_balls_weights_initial.txt", num_neurons, num_dvs_addresses);

	float time = 0;
	int angles[8] = {0,45,90,135,180,225,270,315};
	std::uniform_int_distribution<int> angle_dist(0,7);
	for (int rep=0; rep<num_repetitions; ++rep)
	{
		cout << "rep " << rep << endl;
		//for (float angle=0; angle<360; angle+=45)
		//{
		int angle = angles[angle_dist(generator)];
			cout << "angle " << angle << endl;
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

							for (int j=0; j<num_neurons; ++j)//Synapse synapse : synapses[pixel])
								synapses[(row*image_width+col)*2][j].pre(time);
//							#print row,col,pixel
						}
						else if (image_diff[col][row] < 0)
						{
							off_pixels += 1;

							for (int j=0; j<num_neurons; ++j)//Synapse synapse : synapses[pixel])
								synapses[(row*image_width+col)*2+1][j].pre(time);
//							#print row,col,pixel
						}
					}
				}
//				#print image_diff
				if (on_pixels > 0 || off_pixels > 0)
				{
					cout << "ON: " << on_pixels << ", OFF: " << off_pixels << endl;
				}
				cout << "-------- time = " << time << " ----------" << endl;
				time += dt;
			}
			// add a time-step of 100 ms between each run
			time += 100.0;
		//}
	}

	auto spikes = neurons.get_spikes();
	ofstream file("./results/xnet_balls_spikes.dat",ios::out);
	for (auto pair : spikes)
	{
		file << get<0>(pair) << "," << get<1>(pair) << "\n";
	}
	file.close();
//		#if len(spikes[n]) > 0:
//		#	print n,len(spikes[n])
//		plt.plot(spikes[n],np.ones(len(spikes[n]))*n,'o')
//	for n in range(num_repetitions*8*2):
//		plt.axvline(n*100)
//
//	pickle.dump(spikes,open('spikes.dat','wb'))
//
//	#plt.figure()
//	#record = neurons.get_membrane_potential()
//	#record = np.array(record)
//
//	#for n in range(num_neurons):
//	#	times = []
//	#	membranes = []
//	#	for tpl in record[n]:
//	#		times.append(tpl[0])
//	#		membranes.append(tpl[1])
//	#	plt.plot(times,membranes)
//
//	plt.show()
//
	dump_weights(synapses, "./results/xnet_balls_weights_final.txt", num_neurons, num_dvs_addresses);

	// delete synapses
	for (int i=0; i<num_dvs_addresses; ++i)
		delete[] synapses[i];
	delete[] synapses;
}
//# vim: set noexpandtab
