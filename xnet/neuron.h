#pragma once
#include <vector>
#include "xnet_types.h"
#include <tuple>
#include <math.h>
#include <algorithm>

#define EPSILON 0.0001
using namespace std;

class Synapse;

class Neurons
{
	private:
		vector<tuple<float,float>> spikes;
		vector<vector<Synapse*>> synapses;
		vector<vector<tuple<float,float,float>>> membrane_record;
		vector<float> u;
		vector<Time_t> tlast_update, tlast_spike;
		float tau, Vt;
		int num;
		float Tinhibit, Trefrac, winhibit;
		bool record_membrane;

	public:
	Neurons(int num) : u(num,0.0), membrane_record(num), tlast_update(num,0.0), tlast_spike(num,0.0), synapses(num)
	{
		this->tau = 5; //ms
		this->Vt = 10000; //unit?
		this->Tinhibit = 1.5; //ms
		this->Trefrac = 10.0; //ms
		this->winhibit = 500.0; //unit?
		this->num = num;
		this->record_membrane = false;
		// not necessary for this type:
		//this->spikes = [[] for i in range(num)]
		//this->synapses = [[] for i in range(num)]
		//this->tlast_update = [0 for i in range(num)]
		//this->tlast_spike  = [0 for i in range(num)]

		for (int i=0; i<num; ++i)
		{
			this->membrane_record[i].push_back(make_tuple(0.0,0.0,0.0));
		}
	}

	void evolve(int neuron_number, float weight, Time_t t)
	{
		if (t > (*max_element(tlast_spike.begin(),tlast_spike.end()) + Tinhibit) || t < EPSILON)
		{
			float last_spike = tlast_spike[neuron_number];
			if (((t-last_spike) > Trefrac) || t < EPSILON)
			{
				float last_t = tlast_update[neuron_number];
				float last_u = u[neuron_number];
				u[neuron_number] = last_u*exp(-(t-last_t)/tau) + weight;
				tlast_update[neuron_number] = t;

				if (u[neuron_number] > Vt)
				{
					tlast_spike[neuron_number] = t;
					spikes.push_back(make_tuple(neuron_number,t));
					update_synapses(neuron_number,t);
					for (int n=0; n < num; ++n)
						u[n] = 0;
				}
			}
			if (this->record_membrane)
				this->membrane_record[neuron_number].push_back(make_tuple(t,this->u[neuron_number],weight));
		}
	}

	void update_synapses(int neuron_number, Time_t t);

	vector<tuple<float,float>> get_spikes() const {
		return this->spikes;
	}

	vector<vector<tuple<float,float,float>>> get_membrane_potential()
	{
		return this->membrane_record;
	}

	void register_synapse(unsigned int neuron, Synapse* synapse)
	{
		this->synapses[neuron].push_back(synapse);
	}

	vector<Synapse*> get_synapses(int neuron) const
	{
		return this->synapses[neuron];
	}
};

