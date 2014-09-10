#include "BallCamera.h"
#include <random>
#include "gtest/gtest.h"

using namespace std;

//TEST("Foo","Bar")
void foo_bar()
{
	int	num_repetitions = 2;
	float dt = 1.0;
	int image_width = 16;
	int image_height = 16;
	std::default_random_engine generator;
	float velocity = 0.48;
	float ball_radius = 6.0;

	BallCamera cam {
				3.1416/4.,
				velocity,
				ball_radius,
				image_width,
				image_height
		};

	float time = 0;
	int angles[8] = {0,45,90,135,180,225,270,315};
	std::uniform_int_distribution<int> angle_dist(0,7);

	for (int rep=0; rep<num_repetitions; ++rep)
	{
		int angle = angles[angle_dist(generator)];
		cout << "angle: " << angle << ", time: " << time << endl;
		cam.reset_and_angle(angle,time);
		for (float t=0.0; t<(ball_radius+image_width)/velocity*2; t+=dt)
		{
			auto center = cam.get_ball_center(time);
			cout << center[0] << ", " << center[1] << endl;

			//auto image = cam.generate_image(time);
			//int num_on = 0;
			//for (auto row : image)
			//	for (auto col : row)
			//		if (col > 0)
			//			++num_on;
			//cout << num_on <<endl;

			time += dt;
		}
	}
}

int main()
{
	//::testing::InitGoogleTest(&argc, argv);
	//return RUN_ALL_TESTS();
	foo_bar();
}
