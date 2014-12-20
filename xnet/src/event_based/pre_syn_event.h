#pragma once
#include <queue>
#include "event_based/event.h"

class pre_syn_event : public event {
public:
	pre_syn_event (Time_t t, Id_t pre) : event(t), pre_neuron(pre)
	{
	}
private:
	Id_t pre_neuron;
};
