#pragma once
#include <cmath>
#include "weight.h"
#include "xnet_types.h"

namespace xnet {
	class ExpWeight : public Weight
	{
	public:
		ExpWeight();
		explicit ExpWeight(Current_t w, Current_t wmin, Current_t wmax, Current_t ap, Current_t am);
		virtual void update_neg(Time_t,Timeconst_t);
		virtual void update_pos(Time_t,Timeconst_t);
	private:
	};
}
