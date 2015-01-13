#pragma once
#include <queue>
#include "event_based/event.h"

namespace xnet {
	class post_syn_event : public event {
	public:
		post_syn_event (Time_t t, Id_t post) : event(t,EventType::PST,post)//, post_neuron(post)
		{
		}
	private:
//		Id_t post_neuron;
	};
}
