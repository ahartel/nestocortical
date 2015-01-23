#pragma once
#include <vector>
#include "xnet_types.h"
#include <math.h>
#include <iostream>

using namespace std;

/*
   This calss implements a "camera" that let's a
   ball of _radius_ pass by with _velocity_ in a 2D plane and
   records which pixels are covered by the ball's circle.
   The origin of the coordinate system is at center of the screen
   screen with extensions _image_width_ and _image_height_.
*/

class BallCamera
{

public:
	BallCamera(float angle, float velocity, float radius, int image_width, int image_height);

	vector<vector<bool>> generate_image(Realtime_t t);

	pos2D get_ball_center(Realtime_t t) const;

	float distance(float x, float y, float x_center_dist, float y_center_dist);

	void calculate_ball_start();

	void reset_and_angle(float angle, float t);

private:
	float image_width, image_height;
	float angle, velocity, ball_radius, start_time;
	pos2D ball_start;

};

