#pragma once
#include <queue>
#include "event_based/event.h"

namespace xnet {
	class psp_event : public event {
	public:
		psp_event (Time_t t, Id_t post, Current_t c);
		Current_t get_current() const;
	private:
		Current_t current;
	};
}
