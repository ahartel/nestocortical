#include "weight.h"

namespace xnet
{
	Weight::Weight() : weight(0), gmax(0) {};
	Weight::Weight(Weight_t w, float g) : weight(w), gmax(g) {};
}
