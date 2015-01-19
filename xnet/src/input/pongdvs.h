#pragma once
#include "xnet_types.h"
#include <vector>
#include <tuple>
#include <string>

class PongDVS
{
public:
	PongDVS(int width, int height, pos2D v, float r, float pw);
	PongDVS(int width, int height, pos2D v, float r, float pw, std::string filename);
	std::vector<Spike_t> advance(float t, unsigned int up, unsigned int down);
private:
	int court_width, court_height;
	float half_width, half_height, neg_half_width, neg_half_height;
	pos2D velocity, position;
	float radius, half_paddle_width, paddle_pos, paddle_speed;
	std::string logfile;
	bool log;
	Realtime_t time;
};
