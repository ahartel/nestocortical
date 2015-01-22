#pragma once
#include "xnet_types.h"
#include <vector>
#include <string>

class Pong
{
public:
	Pong(int width, int height, pos2D v, float r, float pw);
	Pong(int width, int height, pos2D v, float r, float pw, std::string filename);
	virtual std::vector<Spike_t> advance(Realtime_t t, float paddle_speed);
protected:
	int court_width, court_height;
	float half_width, half_height, neg_half_width, neg_half_height;
	pos2D velocity, position;
	float radius, half_paddle_width, paddle_pos;
	std::string logfile;
	bool log;
	Realtime_t time;
};
