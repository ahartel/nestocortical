#pragma once
#include <queue>
#include "event_based/event.h"

class psp_event : public event {
public:
	psp_event (Time_t t, Id_t post) : event(t), post_neuron(post)
	{
	}
private:
	Id_t post_neuron;
};
