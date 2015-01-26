#pragma once
#include "xnet_types.h"
#include "pong.h"
#include <vector>
#include <random>
#include <string>

class PongPoisson : public Pong
{
public:
	PongPoisson(int width, int height, pos2D v, float r, float pw);
	PongPoisson(int width, int height, pos2D v, float r, float pw, std::string filename);
	virtual std::vector<Spike_t> advance(Realtime_t t, int paddle_speed);
private:
	float on_rate, off_rate;

	std::default_random_engine generator;
	std::uniform_real_distribution<double> distribution;
};
