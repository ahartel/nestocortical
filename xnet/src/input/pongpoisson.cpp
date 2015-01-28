#include "logger.h"
#include "pongpoisson.h"

PongPoisson::PongPoisson(
		unsigned int width, unsigned int height,
		pos2D v, float r, float pw,
		xnet::Population& input,
		xnet::Population& control
	) :
	Pong(width,height,v,r,pw,input,control),
	on_rate(400.0),
	off_rate(1.0),
	distribution(0.0,1.0)
{
	if (width*height != input_pop.size())
		throw std::out_of_range("The size of the input population passed to the pong input class should equal width*height.");
}

PongPoisson::PongPoisson(
		unsigned int width, unsigned int height,
		pos2D v, float r, float pw, std::string filename,
		xnet::Population& input,
		xnet::Population& control
	) :
	Pong(width,height,v,r,pw,filename,input,control),
	on_rate(400.0),
	off_rate(1.0),
	distribution(0.0,1.0)
{
	if (width*height != input_pop.size())
		throw std::out_of_range("The size of the input population passed to the pong input class should equal width*height.");
}

std::vector<Spike_t> PongPoisson::advance(Realtime_t t, unsigned int target_pixel)
{
	// this function call actually advances the ball and the paddle
	std::vector<Spike_t> output_spikes = Pong::advance(t,target_pixel);

	// the code below only generates the position-related output
	// spikes for the ball
	// x
	unsigned int new_x_pixel = std::get<0>(position)+half_width;
	if (new_x_pixel == court_width)
		new_x_pixel -= 1;

	// y
	unsigned int new_y_pixel = std::get<1>(position)+half_height;
	if (new_y_pixel == court_height)
		new_y_pixel -= 1;

	LOGGER("New pixel: ("<< new_x_pixel << "," << new_y_pixel<<")");

	for (unsigned int i=0; i<court_width; ++i)
	{
		for (unsigned int j=0; j<court_height; ++j)
		{
			if (j == new_y_pixel && i == new_x_pixel)
			{
				if (distribution(generator) < on_rate*t)
					output_spikes.push_back(std::make_tuple(0,input_pop.get(i*court_width+j)));
			}
			//else
			//{
			//	if (distribution(generator) < off_rate*t)
			//		output_spikes.push_back(std::make_tuple(0,input_pop.get(i*court_width+j)));
			//}
		}
	}

	return output_spikes;
}
