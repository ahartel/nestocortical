#pragma once
#include <vector>
#include "xnet_types.h"
#include <math.h>
#include <iostream>

using namespace std;

class BallCamera
{
private:
	int image_width, image_height;
	float angle, velocity, ball_radius, start_time;
	vector<double> ball_start;

public:
	BallCamera(float angle, float velocity, float radius, int image_width=28, int image_height=28)
	{
		this->image_width = image_width;
		this->image_height = image_height;
		this->angle = angle;
		this->velocity = velocity;
		this->ball_radius = radius;
		this->start_time = 0;
		calculate_ball_start();
	}

	vector<vector<bool>> generate_image(Time_t t)
	{
		//cout << ball_start[0] << "," << ball_start[1] << endl;
		auto ball_center = get_ball_center(t);
		//cout << ball_center[0] << "," << ball_center[1] << endl;
		vector<vector<bool>> image(image_height,vector<bool>(image_width,false) );
		//unsigned int cnt = 0;
		for (int x=0; x<image_width; ++x)
		{
			for (int y=0; y<image_height; ++y)
			{
				if (distance(x,y,ball_center) < ball_radius)
				{
					//++cnt;
					image[y][x] = true;
				}
			}
		}
		return image;
	}

	vector<double> get_ball_center(Time_t t) const
	{
		return {
			cos(angle)*velocity*(t-start_time) - ball_start[0],
			sin(angle)*velocity*(t-start_time) - ball_start[1]
		};
	}

	float distance(float x, float y, vector<double> center)
	{
		float dist = sqrt(pow(x-center[0],2)+pow(y-center[1],2));
		//cout << dist << endl;
		return dist;
	}

	void calculate_ball_start()
	{
		ball_start = {cos(angle)*ball_radius*2.0,sin(angle)*ball_radius*2.0};
	}

	void reset_and_angle(float angle, float t)
	{
		this->angle = angle;
		this->start_time = t;
		calculate_ball_start();
	}
};

