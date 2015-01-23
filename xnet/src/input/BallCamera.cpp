#include <tuple>
#include "BallCamera.h"
#include "logger.h"

	BallCamera::BallCamera(float angle, float velocity, float radius, int image_width=28, int image_height=28)
	{
		this->image_width = image_width;
		this->image_height = image_height;
		this->angle = angle/360.*2.*M_PI;
		this->velocity = velocity;
		this->ball_radius = radius;
		this->start_time = 0;
		calculate_ball_start();
	}

	vector<vector<bool>> BallCamera::generate_image(Realtime_t t)
	{
		auto ball_center = get_ball_center(t);
		LOGGER(get<0>(ball_center) << "," << get<1>(ball_center));
		float x_center_distance = image_width/-2.0  - get<0>(ball_center);
		float y_center_distance = image_height/-2.0 - get<1>(ball_center);

		vector<vector<bool>> image(image_height,vector<bool>(image_width,false) );

		for (int x=0; x<image_width; ++x)
		{
			for (int y=0; y<image_height; ++y)
			{
				if (distance(x,y,x_center_distance, y_center_distance) < ball_radius)
				{
					image[y][x] = true;
				}
			}
		}
		return image;
	}

	inline
	pos2D BallCamera::get_ball_center(Realtime_t t) const
	{
		return make_tuple(
			cos(angle)*velocity*(t-start_time) + get<0>(ball_start),
			sin(angle)*velocity*(t-start_time) + get<1>(ball_start)
		);
	}

	inline
	float BallCamera::distance(float x, float y, float x_center_dist, float y_center_dist)
	{
		float x_coord = x_center_dist + x;
		float y_coord = y_center_dist + y;
		float dist = sqrt(pow(x_coord,2)+pow(y_coord,2));
		return dist;
	}

	inline
	void BallCamera::calculate_ball_start()
	{
		// calculate the starting point of the ball's center
		LOGGER("Angle: " << angle << ", cos(angle)=" << cos(angle) << ", sin(angle)=" << sin(angle));
		ball_start = std::make_tuple(-1.0*cos(angle)*(image_width/2.0+ball_radius),-1.0*sin(angle)*(image_height/2.0+ball_radius));
		LOGGER(get<0>(ball_start) << "," << get<1>(ball_start));
	}

	void BallCamera::reset_and_angle(float angle, float t)
	{
		this->angle = angle/360.*2.*M_PI;
		this->start_time = t;
		calculate_ball_start();
	}

