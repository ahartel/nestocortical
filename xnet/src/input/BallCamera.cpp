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

	vector<vector<bool>> BallCamera::generate_image(Time_t t)
	{
		auto ball_center = get_ball_center(t);
		LOGGER(get<0>(ball_center) << "," << get<1>(ball_center));

		vector<vector<bool>> image(image_height,vector<bool>(image_width,false) );

		for (int x=0; x<image_width; ++x)
		{
			for (int y=0; y<image_height; ++y)
			{
				if (distance(x,y,ball_center) < ball_radius)
				{
					image[y][x] = true;
				}
			}
		}
		return image;
	}

	inline
	tuple<double,double> BallCamera::get_ball_center(Time_t t) const
	{
		return make_tuple(
			cos(angle)*velocity*(t-start_time) + get<0>(ball_start),
			sin(angle)*velocity*(t-start_time) + get<1>(ball_start)
		);
	}

	inline
	float BallCamera::distance(float x, float y, tuple<double,double> center)
	{
		float x_coord = image_width/-2.0  + x;
		float y_coord = image_height/-2.0 + y;
		float dist = sqrt(pow(x_coord-get<0>(center),2)+pow(y_coord-get<1>(center),2));
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

