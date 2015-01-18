#include "pongdvs.h"

PongDVS::PongDVS(int width, int height, float v, float r) :
	court_width(width),
	court_height(height),
	velocity(v),
	radius(r)
{

}

std::vector<xnet::event*> PongDVS::advance(float t, std::vector<Spike_t> const& spikes)
{

}
