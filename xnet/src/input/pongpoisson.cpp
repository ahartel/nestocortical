#include "logger.h"
#include "pongpoisson.h"

PongPoisson::PongPoisson(int width, int height, pos2D v, float r, float pw) :
	Pong(width,height,v,r,pw),
	on_rate(400.0),
	off_rate(10.0),
	distribution(0.0,1.0),
	paddle_speed(height/(width/std::get<0>(v)))
{
}

PongPoisson::PongPoisson(int width, int height, pos2D v, float r, float pw, std::string filename) :
	Pong(width,height,v,r,pw,filename),
	on_rate(400.0),
	off_rate(10.0),
	distribution(0.0,1.0)
{
}

std::vector<Spike_t> PongPoisson::advance(Realtime_t t, int target_pixel)
{
	std::vector<Spike_t> output_spikes = Pong::advance(t,target_pixel);

	// x
	int new_x_pixel = int(std::get<0>(position)+half_width);
	if (new_x_pixel == int(court_width))
		new_x_pixel -= 1;

	for (unsigned int i=0; i<court_width; ++i)
	{
		if (i == new_x_pixel)
		{
			if (distribution(generator) < on_rate*t)
				output_spikes.push_back(std::make_tuple(0,i));
		}
		else
		{
			if (distribution(generator) < off_rate*t)
				output_spikes.push_back(std::make_tuple(0,i));
		}
	}

	// y
	int new_y_pixel = int(std::get<1>(position)+half_height);
	if (new_y_pixel == int(court_height))
		new_y_pixel -= 1;

	for (unsigned int i=0; i<court_height; ++i)
	{
		if (i == new_y_pixel)
		{
			if (distribution(generator) < on_rate*t)
				output_spikes.push_back(std::make_tuple(0,court_width+i));
		}
		else
		{
			if (distribution(generator) < off_rate*t)
				output_spikes.push_back(std::make_tuple(0,court_width+i));
		}
	}

	return output_spikes;
}
