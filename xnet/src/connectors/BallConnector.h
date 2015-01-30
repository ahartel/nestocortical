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

	// calculate all input spikes first, and don't do it for every repetition
	// these spikes all start at time 0 and contain 100ms of data
	std::map<int,std::vector<Spike_t>> pre_calc_spikes;
	for (int angle : angles)
	{
		cam.reset_and_angle(angle,0);
		for (Time_t t=0; t<1000; t+=dt)
		{
			auto image = cam.generate_image(float(t)*timebase);
			auto spikes = dvs.calculate_spikes(image);
			for (auto nrn : spikes)
			{
				pre_calc_spikes[angle].push_back(std::make_tuple(t,nrn));
			}
		}
	}

	// do the real simulation with random presentation order
	std::ofstream file(filename_base+"_order",std::ios::out);
	file.close();
	for (int rep=0; rep<num_repetitions; ++rep)
	{
		int angle = angles[angle_dist(generator)];
		file.open(filename_base+"_order",std::ios::app);
		file << angle << "," << float(time)*timebase << "\n";
		file.close();

		for (auto spike : pre_calc_spikes[angle])
		{
			theSimulation.add_event(
				new xnet::pre_syn_event(time+std::get<0>(spike),std::get<1>(spike))
			);
		}
		theSimulation.run_until_empty();

		// add a time-step of 200 ms between each run
		time += 2000;
	}


	theSimulation.print_spikes(filename_base+"_spikes.dat",timebase);
}
