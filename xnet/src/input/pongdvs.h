#pragma once
#include "xnet_types.h"
#include "pong.h"
#include <vector>
#include <string>

class PongDVS : public Pong
{
public:
	PongDVS(int width, int height, pos2D v, float r, float pw);
	PongDVS(int width, int height, pos2D v, float r, float pw, std::string filename);
	virtual std::vector<Spike_t> advance(Realtime_t t, float paddle_speed);
private:

};
