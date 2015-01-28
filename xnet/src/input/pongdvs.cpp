#include "logger.h"
#include "pongdvs.h"

PongDVS::PongDVS(
		int width, int height,
		pos2D v, float r, float pw,
		xnet::Population& input,
		xnet::Population& control
	) :
	Pong(width,height,v,r,pw,input,control)
{
}

PongDVS::PongDVS(
		int width, int height,
		pos2D v, float r, float pw,
		std::string filename,
		xnet::Population& input,
		xnet::Population& control
	) :
	Pong(width,height,v,r,pw,filename,input,control)
{
}

std::vector<Spike_t> PongDVS::advance(Realtime_t t, float paddle_speed)
{
	int old_pixel = int(std::get<1>(position)+half_height);
	if (old_pixel == int(court_height))
		old_pixel -= 1;

	std::vector<Spike_t> output_spikes = Pong::advance(t,paddle_speed);

	int new_pixel = int(std::get<1>(position)+half_height);
	if (new_pixel == int(court_height))
		new_pixel -= 1;

	if (new_pixel != old_pixel)
	{
		LOGGER("new: " << new_pixel << ", old:" << old_pixel);
		output_spikes.push_back(std::make_tuple(0,new_pixel*2));
		output_spikes.push_back(std::make_tuple(0,old_pixel*2+1));
	}

	return output_spikes;
}
