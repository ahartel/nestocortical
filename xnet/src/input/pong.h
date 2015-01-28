#pragma once
#include "xnet_types.h"
#include "event_based/population.h"
#include <vector>
#include <string>

class Pong
{
public:
	Pong(
		unsigned int width, unsigned int height,
		pos2D v, float r, float pw,
		xnet::Population&, xnet::Population&);
	Pong(
		unsigned int width, unsigned int height,
		pos2D v, float r, float pw,
		std::string filename,
		xnet::Population&, xnet::Population&);

	virtual std::vector<Spike_t> advance(Realtime_t t, unsigned int target_pixel);
	unsigned int get_court_width() const;
	unsigned int get_court_height() const;
	pos2D get_velocity() const;
protected:
	unsigned int court_width, court_height;
	float half_width, half_height, neg_half_width, neg_half_height;
	pos2D velocity, position;
	float radius, half_paddle_width, paddle_pos;
	std::string logfile;
	bool log;
	Realtime_t time;
	float paddle_speed;
	xnet::Population& input_pop, control_pop;
};
