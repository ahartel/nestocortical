#pragma once
#include <vector>
#include "xnet_types.h"
#include <tuple>
#include <math.h>
#include <algorithm>
#include <iostream>

#define EPSILON 0.0001
using namespace std;

namespace xnet {
	class Synapse;

	class Neurons
	{
		private:
			vector<tuple<float,float>> spikes;
			Synapse*** synapses;
			vector<vector<tuple<float,float,float>>> membrane_record;
			vector<float> u;
			vector<Time_t> tlast_update, tlast_spike;
			float tau, Vt;
			int num_neurons, num_synapses;
			int* synapse_count;
			float Tinhibit, Trefrac, winhibit;
			bool record_membrane;

		public:
		Neurons(int num, int num_synapses) : u(num,0.0), membrane_record(num), tlast_update(num,0.0), tlast_spike(num,0.0), synapse_count(0)
		{
			this->tau = 5; //ms
			this->Vt = 10000; //unit?
			this->Tinhibit = 1.5; //ms
			this->Trefrac = 10.0; //ms
			this->winhibit = 500.0; //unit?
			this->num_neurons = num;
			this->num_synapses = num_synapses;
			this->record_membrane = false;
			// not necessary for this type:
			//this->spikes = [[] for i in range(num)]
			//this->synapses = [[] for i in range(num)]
			//this->tlast_update = [0 for i in range(num)]
			//this->tlast_spike  = [0 for i in range(num)]

			synapses = new Synapse**[num];
			synapse_count = new int[num];

			for (int i=0; i<num; ++i)
			{
				synapse_count[i] = 0;
				synapses[i] = new Synapse*[num_synapses];
				this->membrane_record[i].push_back(make_tuple(0.0,0.0,0.0));
			}
		}

		Neurons(int num, int num_synapses, float tleak, float vt, float tinh, float trefr) :
			u(num,0.0),
			membrane_record(num),
			tlast_update(num,0.0),
			tlast_spike(num,0.0),
			synapse_count(0),
			tau(tleak),
			Vt(vt),
			Tinhibit(tinh),
			Trefrac(trefr)
		{
			this->winhibit = 500.0; //unit?
			this->num_neurons = num;
			this->num_synapses = num_synapses;
			this->record_membrane = false;
			// not necessary for this type:
			//this->spikes = [[] for i in range(num)]
			//this->synapses = [[] for i in range(num)]
			//this->tlast_update = [0 for i in range(num)]
			//this->tlast_spike  = [0 for i in range(num)]

			synapses = new Synapse**[num];
			synapse_count = new int[num];

			for (int i=0; i<num; ++i)
			{
				synapse_count[i] = 0;
				synapses[i] = new Synapse*[num_synapses];
				this->membrane_record[i].push_back(make_tuple(0.0,0.0,0.0));
			}
		}

		~Neurons()
		{
			for (int i=0; i<num_neurons; ++i)
				delete[] synapses[i];
			delete[] synapses;
			delete[] synapse_count;
		}

		void evolve(int neuron_number, float weight, Time_t t);

		void update_synapses(int neuron_number, Time_t t);

		vector<tuple<float,float>> get_spikes() const {
			return this->spikes;
		}

		vector<vector<tuple<float,float,float>>> get_membrane_potential()
		{
			return this->membrane_record;
		}


		void register_synapse(unsigned int neuron, Synapse* synapse);
		Synapse** get_synapses(int neuron) const;
	};
}

//class Neurons_softinhibit(Neurons):
//	def __init__(self,num):
//		super(Neurons_softinhibit,self).__init__(num)
//
//	def evolve(self,neuron_number,weight,t):
//		last_spike = self.__tlast_spike[neuron_number]
//		if (t-last_spike) > self.__Trefrac:
//			last_t = self.__tlast_update[neuron_number]
//			last_u = self.__u[neuron_number]
//			self.__u[neuron_number] = last_u*math.exp(-(t-last_t)/self.__tau) + weight
//			self.__tlast_update[neuron_number] = t
//
//			if self.__u[neuron_number] > self.__Vt:
//				self.__tlast_spike[neuron_number] = t
//				self.__spikes[neuron_number].append(t)
//				self.update_synapses(neuron_number,t)
//				for n in range(self.__num):
//					if n == neuron_number:
//						self.__u[n] = 0
//					else:
//						self.__u[n] -= self.__winhibit
//
//		if self.__record_membrane:
//			self.__membrane_record[neuron_number].append((t,self.__u[neuron_number],weight))



