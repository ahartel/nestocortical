#include "synapse.h"
#include "neuron.h" 

void Synapse::pre(Time_t t)
{
	last_pre_spike = t;
	neurons->evolve(psn,w,t);
}
//	def pre(self,t):
//		#print 'sending spike to neuron ',self.__psn,' with weight ',self.__w
//		self.__last_pre_spike = t
//		self.__neurons.evolve(self.__psn,self.__w,t)

void Synapse::register_at_neuron()
{
	neurons->register_synapse(psn, this);
}
//	def register_at_neuron(self):
//		self.__neurons.register_synapse(self.__psn,self.update)
