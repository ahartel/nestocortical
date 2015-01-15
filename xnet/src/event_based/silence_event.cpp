#include "silence_event.h"

namespace xnet
{
	silence_event::silence_event (Time_t t, Id_t post) :
		event(t,EventType::SIL,post)
	{
	}
}

