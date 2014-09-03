#include "neuron.h"
#include "synapse.h"
#include "DVS.h"
#include "BallCamera.h"
#include "load_aer.h"

#include <tuple>
#include <iostream>

using namespace std;

int main(int argc, char* argv[])
{
	// define geometry
	int num_neurons = 48;
	int image_width  = 128;
	int image_height = 128;
	int num_dvs_addresses = 2 * image_width * image_height;
	// load data
	auto data_time = load_aer(argv[1]);
	// init neurons
	Neurons neurons(num_neurons);
	// synaptic parameters are random
	std::default_random_engine generator;
	std::normal_distribution<float> weight_distribution(800.0,160.0);
	std::normal_distribution<float> am_distribution(100.0,20.0);
	std::normal_distribution<float> ap_distribution(50.0,10.0);
	std::normal_distribution<float> wmin_distribution(1.0,0.2);
	std::normal_distribution<float> wmax_distribution(1000.0,200.0);
	// init synapses
	vector<vector<Synapse>> synapses;
	for (int i=0; i<num_dvs_addresses; ++i)
	{
		synapses.push_back({});
		for (int j=0; j<num_neurons; ++j)
			synapses.back().push_back(
				Synapse(i*num_dvs_addresses+j,&neurons,j,
						weight_distribution(generator),
						am_distribution(generator),
						ap_distribution(generator),
						wmin_distribution(generator),
						wmax_distribution(generator)
						));
	}

	auto max_time = get<1>(data_time.back());

	for (int run=0; run<10; ++run)
	{
		cout << "Run #" << run << endl;
		for (auto event : data_time)
		{
			auto time = get<1>(event) + max_time*run;
			for (Synapse synapse : synapses[get<0>(event)])
			{
				synapse.pre(time);
			}
			if (time % 1000000 == 0)
				cout << "time = " << time << endl;
			//if (time >= 100000000)
			//	break;
		}
	}

	auto spikes = neurons.get_spikes();
	ofstream file("xnet_traffic_spikes.dat",ios::out);
	for (auto pair : spikes)
	{
		file << get<0>(pair) << "," << get<1>(pair) << "\n";
	}
	file.close();

}
