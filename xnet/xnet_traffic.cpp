#include "neuron.h"
#include "synapse.h"
#include "DVS.h"
#include "BallCamera.h"
#include "load_aer.h"

#include <tuple>
#include <iostream>
#include <iomanip>
#include <cstdlib>

using namespace std;

typedef Synapse** SynapseArray;

// define geometry
int num_neurons = 60;
int image_width  = 128;
int image_height = 128;
int num_dvs_addresses = 2 * image_width * image_height;

void dump_weights(SynapseArray const& synapses, string filename)
{
	// write weights to a file with one line per line of weights in the image
	// one neuron gets image_height lines with image_width entries
	// after the lines of one neuron have been written, the next neuron starts immediately
	vector<vector<float>> neuron_weights(num_neurons);
	//for (auto syngroup : synapses)
	for (int n=0; n<num_dvs_addresses; ++n)
	{
		for (int i=0; i<num_neurons; ++i)
		{
			neuron_weights[i].push_back(synapses[n][i].get_weight());
		}
	}
	ofstream weight_file(filename,ios::out);
	weight_file << fixed << setprecision(2);
	for (auto neuron : neuron_weights)
	{
		unsigned int cnt=0;
		for (int i=0; i<num_dvs_addresses; i=i+2) {
			if ((i > 0 && (i+2)/2 % image_width == 0 ) || i == num_dvs_addresses-2)
			{
				weight_file << neuron[i] << "\n";
				++cnt;
			}
			else
				weight_file << neuron[i] << " ";
		}
	}
	weight_file.close();
}

int main(int argc, char* argv[])
{
	// load data
	int max_load_time = -1;
	if (argc > 2)
		max_load_time = atoi(argv[2]);

	auto data_time = load_aer(argv[1], max_load_time);
	// init neurons
	Neurons neurons(num_neurons, num_dvs_addresses);
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
		//synapses.push_back({});
		synapses[i] = new Synapse[num_neurons];
		for (int j=0; j<num_neurons; ++j)
		{
			//if (j==19)
			//	cout << "Synapse ID " << i*num_neurons+j << " connects to neuron " << j << endl;
			synapses[i][j].set_parameters(
				        i*num_neurons+j,&neurons,j,
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

	dump_weights(synapses, "xnet_traffic_weights_initial.txt");

	//syns = neurons.get_synapses(1);
	//cout << syns.size() << endl;
	//cout << syns.back()->get_id() << endl;
	//cout << syns.back()->get_psn() << endl;
	//return 0;

	auto max_time = get<1>(data_time.back());

	for (int run=0; run<1; ++run)
	{
		cout << "Run #" << run << endl;
		for (auto event : data_time)
		{
			auto time  = get<1>(event) + max_time*run;
			auto pixel = get<0>(event);
			unsigned int neuron_cnt = 0;
			//for (Synapse synapse : synapses[pixel])
			for (int j=0; j<num_neurons; ++j)//Synapse synapse : synapses[pixel])
			{
				//cout << "Sending spike to synapse[" << pixel << "][" << neuron_cnt << "]" << endl;
				synapses[pixel][j].pre(time);
				++neuron_cnt;
			}

			if (time > 0 && time % 10000 == 0)
				cout << "time = " << time << endl;

		}
	}

	auto spikes = neurons.get_spikes();
	ofstream spike_file("xnet_traffic_spikes.dat",ios::out);
	for (auto pair : spikes)
	{
		spike_file << get<0>(pair) << "," << get<1>(pair) << "\n";
	}
	spike_file.close();

	dump_weights(synapses, "xnet_traffic_weights_final.txt");
}


