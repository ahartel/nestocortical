#pragma once
#include "xnet_types.h"
#include <iostream>

using namespace std;

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

	void pre(Time_t t)
	{
		last_pre_spike = t;
		if (psn == 19)
			cout << "Sending spike to neuron " << psn << " @time " << t << endl;
		neurons->evolve(psn,w,t);
	}
//	def pre(self,t):
//		#print 'sending spike to neuron ',self.__psn,' with weight ',self.__w
//		self.__last_pre_spike = t
//		self.__neurons.evolve(self.__psn,self.__w,t)

	void register_at_neuron()
	{
		neurons->register_synapse(psn, this);
	}
//	def register_at_neuron(self):
//		self.__neurons.register_synapse(self.__psn,self.update)

	void update(Time_t t)
	{
		cout << "Updating synapse ID " << id << " to neuron " << psn << endl;
		if (last_pre_spike > 0)
			cout << "update in synapse with last_pre_spike=" << last_pre_spike << " and t=" << t << endl;
		if (t-last_pre_spike > TLTP && w > wmin)
		{
			w -= alpha_minus;
		}
		else if (t-last_pre_spike <= TLTP && w < wmax)
		{
			w += alpha_plus;
		}

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
};


