#undef DEBUG_OUTPUT

#include "neuron.h"
#include "synapse.h"
#include "DVS.h"
#include "BallCamera.h"
#include "load_aer.h"

#include <tuple>
#include <iostream>
#include <iomanip>
#include <cstdlib>
#include <fstream>

using namespace std;
using namespace xnet;

// define geometry
int num_neurons = 60;
int image_width  = 128;
int image_height = 128;
int num_dvs_addresses = 2 * image_width * image_height;

int main(int argc, char* argv[])
{
	// load data
	int max_load_time = -1;
	if (argc > 2)
		max_load_time = atoi(argv[2]);

	auto data_time = load_aer(argv[1], max_load_time);
	auto max_time = get<1>(data_time.back());
	cout << data_time.size() << " events in " << max_time << " us" << endl;
	// init neurons
	Neurons neurons(num_neurons, num_dvs_addresses,187000.0/*tau*/,1060000.0/*Vt*/,10200.0/*Tinhibit*/,517000.0/*Trefrac*/);
	// synaptic parameters are random
	std::default_random_engine generator;
	std::normal_distribution<float> weight_distribution(800.0,160.0);
	std::normal_distribution<float> am_distribution(100.0,20.0);
	std::normal_distribution<float> ap_distribution(50.0,10.0);
	std::normal_distribution<float> wmin_distribution(1.0,0.2);
	std::normal_distribution<float> wmax_distribution(1000.0,200.0);
	// init synapses
	SynapseArray synapses;
	synapses = new Synapse*[num_dvs_addresses];
	for (int i=0; i<num_dvs_addresses; ++i)
	{
		synapses[i] = new Synapse[num_neurons];
		for (int j=0; j<num_neurons; ++j)
		{
			synapses[i][j].set_parameters(
				        i*num_neurons+j,&neurons,j,14700.0/*TLTP*/,
						weight_distribution(generator),
						am_distribution(generator),
						ap_distribution(generator),
						wmin_distribution(generator),
						wmax_distribution(generator)
					);
		}
	}

	//auto syns = neurons.get_synapses(19);
	////cout << "Size:" << syns.size() << endl;
	//for (int i=0; i<10; ++i)
	//{
	//	cout << syns[i]->get_id() << endl;
	//	cout << syns[i]->get_psn() << endl;
	//}

	dump_weights(synapses, "./results/xnet_traffic_weights_initial.txt", num_neurons, num_dvs_addresses);

	//syns = neurons.get_synapses(1);
	//cout << syns.size() << endl;
	//cout << syns.back()->get_id() << endl;
	//cout << syns.back()->get_psn() << endl;
	//return 0;


	for (int run=0; run<5; ++run)
	{
		cout << "Run #" << run << endl;
		for (auto event : data_time)
		{
			auto time  = get<1>(event) + max_time*run;
			auto pixel = get<0>(event);

			for (int j=0; j<num_neurons; ++j)//Synapse synapse : synapses[pixel])
			{
#ifdef DEBUG_OUTPUT
				if (j==19)
					cout << "Sending spike to synapse[" << pixel << "][" << j << "]" << endl;
#endif
				synapses[pixel][j].pre(time);
			}

			if (time > 0 && time % 100000 == 0)
				cout << "time = " << time << endl;

		}
	}

	auto spikes = neurons.get_spikes();
	ofstream spike_file("./results/xnet_traffic_spikes.dat",ios::out);
	for (auto pair : spikes)
	{
		spike_file << get<0>(pair) << "," << get<1>(pair) << "\n";
	}
	spike_file.close();

	dump_weights(synapses, "./results/xnet_traffic_weights_final.txt", num_neurons, num_dvs_addresses);

	// delete synapses
	for (int i=0; i<num_dvs_addresses; ++i)
		delete[] synapses[i];
	delete[] synapses;
}


