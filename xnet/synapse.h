#pragma once
#include <iostream>
#include <fstream>
#include <iomanip>
#include "xnet_types.h"
#include "neuron.h"

using namespace std;

namespace xnet {
	class Synapse
	{
		private:
			Neurons* neurons;
			unsigned int psn, id;
			float w, wmin, wmax;
			Time_t last_pre_spike;
			float alpha_minus, alpha_plus;
			Time_t TLTP;


		public:

		Synapse()
		{
			w = 800; // TODO: should be normally distributed with mu=800, sigma=160
			TLTP = 2; // ms
			alpha_minus = 100; // TODO: should be normally distributed with mu=100, std=20
			alpha_plus  = 50; // TODO: should be normally distributed with mu=50, std=10
			wmin = 1.0; // TODO: should be normally distributed with mu=1.0, std=0.2
			wmax = 1000.0; // TODO: should be normally distributed with mu=1000, std=200
			last_pre_spike = 0;
		}

		Synapse(unsigned int i, Neurons* neurons_ref, unsigned int post_neuron) :
				neurons(neurons_ref),
				psn(post_neuron),
				id(i),
				last_pre_spike(0)
		{
			w = 800; // TODO: should be normally distributed with mu=800, sigma=160
			TLTP = 2; // ms
			alpha_minus = 100; // TODO: should be normally distributed with mu=100, std=20
			alpha_plus  = 50; // TODO: should be normally distributed with mu=50, std=10
			wmin = 1.0; // TODO: should be normally distributed with mu=1.0, std=0.2
			wmax = 1000.0; // TODO: should be normally distributed with mu=1000, std=200

			register_at_neuron();
		}

		Synapse(unsigned int i,
				Neurons* neurons_pointer,
				unsigned int post_neuron,
				float weight=800.0,
				float aminus=100.0,
				float aplus=50.0,
				float wmin_=1.0,
				float wmax_=1000.0
			) : neurons(neurons_pointer),
				psn(post_neuron),
				id(i),
				last_pre_spike(0),
				w(weight),
				alpha_minus(aminus),
				alpha_plus(aplus),
				wmin(wmin_),
				wmax(wmax_)
		{
			TLTP = 2; // ms

			register_at_neuron();
		}

		void set_parameters(unsigned int i,
				Neurons* neurons_pointer,
				unsigned int post_neuron,
				float weight=800.0,
				float aminus=100.0,
				float aplus=50.0,
				float wmin_=1.0,
				float wmax_=1000.0
			)
		{
			neurons = neurons_pointer;
			psn = post_neuron;
			id = i;
			w = weight;
			alpha_minus = aminus;
			alpha_plus = aplus;
			wmin = wmin_;
			wmax = wmax_;
			TLTP = 2; // ms

			register_at_neuron();
		}

	//	def __init__(self,id,neurons,post_neuron):
	//		self.__w = np.random.normal(800,160)
	//		self.__last_pre_spike = 0
	//		self.__TLTP = 2 # ms
	//		self.__alpha_minus = np.random.normal(100,20)
	//		self.__alpha_plus = np.random.normal(50,10)
	//		self.__wmin = np.random.normal(1,0.2)
	//		self.__wmax = np.random.normal(1000,200)
	//
	//		self.register_at_neuron()

		void pre(Time_t t);

		void register_at_neuron();

		void update(Time_t t)
		{
			auto delta_t = t-last_pre_spike;

			#ifdef DEBUG_OUTPUT
			cout << "Updating synapse ID " << id << " to neuron " << psn << " with weight " << w << " and wmax " << wmax << endl;
			cout << "update in synapse with last_pre_spike=" << last_pre_spike << " and t=" << t << " (delta_t:" << delta_t << ")" << endl;
			#endif

			if (delta_t < 0)
			{
				if (w > wmin)
				{
			#ifdef DEBUG_OUTPUT
					cout << " depressing synapse, new weight: " << w << endl;
			#endif
					w -= alpha_minus;
				}
			#ifdef DEBUG_OUTPUT
				else
				{
					cout << "Not doing anything 1" << endl;
				}
			#endif
			}
			else if (delta_t >=0)
			{
				if (delta_t > TLTP && w > wmin)
				{
			#ifdef DEBUG_OUTPUT
					cout << " depressing synapse, new weight: " << w << endl;
			#endif
					w -= alpha_minus;
				}
				else if (delta_t <= TLTP && w < wmax)
				{
			#ifdef DEBUG_OUTPUT
					cout << " potentiating synapse, new weight: "<< w << endl;
			#endif
					w += alpha_plus;
				}
			#ifdef DEBUG_OUTPUT
				else
				{
					cout << "Not doing anything 2" << endl;
				}
			#endif
			}
			#ifdef DEBUG_OUTPUT
			else
			{
				cout << "Not doing anything 3" << endl;
			}
			#endif

			if (w > wmax)
				w = wmax;
			else if (w < wmin)
				w = wmin;
		}
	//	def update(self,t):
	//		if t-self.__last_pre_spike > self.__TLTP and self.__w > self.__wmin:
	//			self.__w -= self.__alpha_minus
	//		elif t-self.__last_pre_spike <= self.__TLTP and self.__w < self.__wmax:
	//			self.__w += self.__alpha_plus
	//
	//		if self.__w > self.__wmax:
	//			self.__w = self.__wmax
	//		elif self.__w < self.__wmin:
	//			self.__w = self.__wmin

		float get_weight() const
		{
			return w;
		}

		unsigned int get_id() const
		{
			return id;
		}

		unsigned int get_psn() const
		{
			return psn;
		}
	};

	typedef Synapse** SynapseArray;

	void dump_weights(SynapseArray const& synapses, string filename, size_t num_neurons, size_t num_inputs, size_t num_inputs_per_row);
}

