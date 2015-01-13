#pragma once
#include <queue>
#include "event_based/event.h"

namespace xnet {
	class psp_event : public event {
	public:
		psp_event (Time_t t, Id_t post, Current_t c) :
			event(t,EventType::PSP,post),
			current(c)
		{
		}
		//virtual void processEvent ();
		Current_t get_current() const;
	private:
		Current_t current;
	};
}
