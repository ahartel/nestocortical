#pragma once
#include <queue>
#include "event_based/event.h"

namespace xnet {
	class psp_event : public event {
	public:
		psp_event (Time_t t, Id_t post, Current_t c) :
			event(t),
			post_neuron(post),
			current(c)
		{
		}
		virtual void processEvent ();
	private:
		Id_t post_neuron;
		Current_t current;
	};
}
