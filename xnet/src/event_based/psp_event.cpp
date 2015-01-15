#include "logger.h"
#include "neuron.h"
#include "psp_event.h"

namespace xnet
{
	psp_event::psp_event (Time_t t, Id_t post, Current_t c) :
		event(t,EventType::PSP,post),
		current(c)
	{
	}

	Current_t psp_event::get_current() const
	{
		return current;
	}
}
