#include <map>
#include <gtest/gtest.h>
#include <cstdlib>
#include <vector>
#include <tuple>
#include <iostream>
#include <random>

#include "logger.h"
#include "DVS.h"
#include "BallCamera.h"

using namespace std;

TEST(INPUT,BALL_TRAJECTORY)
{
	int image_width = 16;
	int image_height = 16;
	float dt = 1.0;
	int	num_repetitions = 2;
	float velocity = 0.48;
	float ball_radius = 6.0;

	DVS dvs(image_width,image_height);
	BallCamera cam {
            0.0, // angle in degrees
            velocity,
            ball_radius,
            image_width,
            image_height
	};


	float time = 0;
	int angles[2] = {0,180};

	for (int rep=0; rep<num_repetitions; ++rep)
	{
		int angle = angles[rep];
		LOGGER("-------- repetition = " << rep << ", time = " << time
			<< ", angle = " << angle << " ----------");

		cam.reset_and_angle(angle,time);

		for (float t=0.0; t<100.0; t+=dt)
		{
			auto image = cam.generate_image(time);

			auto spikes = dvs.calculate_spikes(image);
			for (auto spike : spikes)
			{
				// first off spike should occur after 25 timesteps
				if (t < 13.0)
					EXPECT_EQ(spike%2,0);

				// with the given ball radius, direction and image
				// dimensions the first row's pixel should never
				// register a spike
				if (spike%2)
					LOGGER("OFF spike in " << spike);
				else
					LOGGER("ON spike in " << spike);

				EXPECT_GE(spike,32);
				EXPECT_LT(spike,480);
			}

			time += dt;
		}
		// add a time-step of 100 ms between each run
		time += 100.0;
	}

}

int main(int argc, char** argv) {
	::testing::InitGoogleTest(&argc, argv);
	::testing::FLAGS_gtest_death_test_style = "fast";
	return RUN_ALL_TESTS();
}

//# vim: set noexpandtab
