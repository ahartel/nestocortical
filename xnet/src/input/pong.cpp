#include "pong.h"
#include <fstream>

Pong::Pong(int width, int height, pos2D v, float r, float pw) :
	court_width(width),
	court_height(height),
	half_width(float(width)/2.0),
	half_height(float(height)/2.0),
	neg_half_width(float(width)/-2.0),
	neg_half_height(float(height)/-2.0),
	velocity(v),
	radius(r),
	half_paddle_width(pw/2.0),
	time(0)
{
	// start in the middle of the court at the left edge
	position = std::make_tuple(court_width/-2.0, 0);
	// also start the paddle in the middle
	paddle_pos = 0.0;
}

Pong::Pong(int width, int height, pos2D v, float r, float pw, std::string filename) :
	Pong(width,height,v,r,pw)
{
	log = true;
	logfile = filename;

	std::ofstream file(filename,std::ios::out);
	file << "time,x,y,paddle" << "\n";
	file << 0 << "," << std::get<0>(position) << "," << std::get<1>(position) << "," << paddle_pos << "\n";
	file.close();
}

std::vector<Spike_t> Pong::advance(Realtime_t t, float paddle_speed)
{
	std::vector<Spike_t> output_spikes;

	auto new_x = std::get<0>(position) + std::get<0>(velocity) * t;
	auto new_y = std::get<1>(position) + std::get<1>(velocity) * t;

	auto new_pp = paddle_pos + paddle_speed;
	if (new_pp + half_paddle_width > half_height)
		paddle_pos = half_height-half_paddle_width;
	else if (new_pp < half_paddle_width - half_height)
		paddle_pos = (-1.0)*half_height + half_paddle_width;
	else paddle_pos = new_pp;

	time += t;

	// y-bouncing is easy
	if (new_y >= half_height)
	{
		new_y -= new_y - half_height;
		std::get<1>(velocity) = std::get<1>(velocity)*-1.0;
	}
	else if (new_y <= neg_half_height)
	{
		new_y -= new_y + half_height;
		std::get<1>(velocity) = std::get<1>(velocity)*-1.0;
	}

	// x-bouncing needs to emit spikes
	if (new_x >= half_width)
	{
		int new_y_pixel = int(new_y+half_height);
		if (new_y_pixel == int(court_height))
			new_y_pixel -= 1;

		output_spikes.push_back(std::make_tuple(time,court_width+court_height+new_y_pixel));

		// calculate position
		new_x -= new_x - half_width;
		std::get<0>(velocity) = std::get<0>(velocity)*-1.0;
	}
	else if (new_x <= neg_half_width)
	{
		new_x -= new_x + half_width;
		std::get<0>(velocity) = std::get<0>(velocity)*-1.0;
	}

	position = std::make_tuple(new_x,new_y);

	if (log)
	{
		std::ofstream file(logfile,std::ios::app);
		file << time << "," << new_x << "," << new_y << "," << paddle_pos << "\n";
		file.close();
	}

	return output_spikes;
}
