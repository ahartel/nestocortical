#pragma once
#include <queue>
#include "event_based/event.h"

namespace xnet {
	class silence_event : public event {
	public:
		silence_event (Time_t t, Id_t post);
	private:
	};
}
