#pragma once
#include <queue>
#include "event_based/event.h"

namespace xnet
{
	class pre_syn_event : public event {
	public:
		pre_syn_event (Time_t t, Id_t pre) : event(t,EventType::PRE,pre)//, pre_neuron(pre)
		{
		}
	//	virtual void processEvent ();
	//private:
	//	Id_t pre_neuron;
	};
}
