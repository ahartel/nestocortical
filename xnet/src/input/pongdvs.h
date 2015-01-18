#pragma once
#include "event.h"
#include <vector>

class PongDVS
{
public:
	PongDVS(int width, int height, float v, float r);
	std::vector<xnet::event*> advance(float t, std::vector<Spike_t> const& spikes);
private:
	int court_width, court_height;
	float velocity, radius;
};
