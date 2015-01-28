#pragma once
#include "xnet_types.h"
#include "pong.h"
#include <vector>
#include <random>
#include <string>

class PongPoisson : public Pong
{
public:
	PongPoisson(
		unsigned int width, unsigned int height,
		pos2D v, float r, float pw,
		xnet::Population& input,
		xnet::Population& control
	);
	PongPoisson(
		unsigned int width, unsigned int height,
		pos2D v, float r, float pw,
		std::string filename,
		xnet::Population& input,
		xnet::Population& control
	);
	virtual std::vector<Spike_t> advance(Realtime_t t, unsigned int target_pixel);
private:
	float on_rate, off_rate;

	std::default_random_engine generator;
	std::uniform_real_distribution<double> distribution;
};
