#pragma once
#include <cmath>
#include "weight.h"
#include "xnet_types.h"

namespace xnet {
	class RectWeight : public Weight
	{
	public:
		RectWeight();
		explicit RectWeight(Current_t w, Current_t wmin, Current_t wmax, Current_t ap, Current_t am);
		virtual void update_neg();
		virtual void update_pos();
	private:
	};
}
