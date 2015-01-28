#pragma once

template<typename SIM>
inline
void runBallConnector(SIM& theSimulation, BallCamera& cam, DVS& dvs, std::string filename_base, int num_repetitions)
{
	Time_t time = 0;
	std::default_random_engine generator;
	Time_t dt = 10;
	float timebase = 1.0e-4;

	int angles[8] = {0,45,90,135,180,225,270,315};
	std::uniform_int_distribution<int> angle_dist(0,7);

	std::ofstream file(filename_base+"/xnet_balls_order",std::ios::out);
	file.close();
	for (int rep=0; rep<num_repetitions; ++rep)
	{
		int angle = angles[angle_dist(generator)];
		file.open(filename_base+"/xnet_balls_order",std::ios::app);
		file << angle << "," << float(time)*timebase << "\n";
		file.close();

		cam.reset_and_angle(angle,float(time)*timebase);

		for (Time_t t=0; t<1000; t+=dt)
		{
			auto image = cam.generate_image(float(time)*timebase);

			auto spikes = dvs.calculate_spikes(image);
			for (auto spike : spikes)
			{
				theSimulation.add_event(new xnet::pre_syn_event(time,spike));
			}
			time += dt;
		}
		// add a time-step of 100 ms between each run
		time += 1000;
	}

	LOGGER(theSimulation.get_spikes().size());
	//theSimulation.run(10000);
	theSimulation.run_until_empty();

	theSimulation.print_spikes(filename_base+"/xnet_balls_spikes.dat",timebase);
}
