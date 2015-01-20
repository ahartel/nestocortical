#pragma once
#include <cmath>
#include "xnet_types.h"

namespace xnet {
	class Weight
	{
	public:
		Weight();
		explicit Weight(Current_t w, Current_t wmin, Current_t wmax, Current_t ap, Current_t am);
		Current_t calc_current() const;
		void update_neg();
		void update_pos();
	private:
		//static const Weight_t wmax = std::pow(2,sizeof(Weight_t))-1;
		Current_t w;
		Current_t wmin;
		Current_t wmax;
		Current_t ap;
		Current_t am;
	};
}
