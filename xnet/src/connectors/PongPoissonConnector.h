#pragma once

template<typename T>
size_t max(std::vector<T> const& input)
{
	T max_value = 0;
	std::size_t max_pos = 0;
	for (size_t i=0; i<input.size(); ++i)
	{
		if (input[i] > max_value)
		{
			max_value = input[i];
			max_pos = i;
		}
	}
	return max_pos;
}

template<typename SIM>
inline
void runPongPoissonConnector (SIM& theSimulation, PongPoisson& pong, xnet::Population const& output, std::string filename_base, int num_repetitions)
{
	float timebase = 1.0e-4;
	Time_t dt = 10;
	Time_t time = 0;
	int last_guess(0), new_guess(0);

	// one repetition consists of letting the ball bounce back and forth once
	for (int rep=0; rep<num_repetitions; ++rep)
	{
		LOGGER("Repetition " << rep);
		// this is how long it takes to bounce the ball back and forth once
		for (Time_t t=0; t<pong.get_court_width()/fabs(std::get<0>(pong.get_velocity()))*2*10000; t+=dt)
		{
			auto output_spikes = theSimulation.get_new_spikes();
			std::vector<int> guess(pong.get_court_height());
			// collect the spikes of the output neurons and count them
			for (auto spike : output_spikes)
			{
				for (unsigned int n=0; n<output.size();++n)
				{
					if (std::get<1>(spike) == output.get(n))
					{
						guess[n] += 1;
					}
				}
			}
			if (std::any_of(guess.begin(), guess.end(), [](int i){return i>0;}))
			{
				new_guess = max(guess);
				last_guess = new_guess;
			}
			else
			{
				new_guess = last_guess;
			}
			// advance the pong simulation by 1 ms
			auto input_spikes = pong.advance(0.001,new_guess);
			LOGGER("Processing input spikes, size: "<<input_spikes.size());
			// present the newly generated input data to the network
			for (auto spike : input_spikes)
			{
				Id_t nrn = std::get<1>(spike);
				Time_t target_time = time + theSimulation.get_neuron_pointer(nrn)->get_delay();
				theSimulation.add_event(new xnet::pre_syn_event(target_time,nrn));
				theSimulation.add_event(new xnet::pre_syn_event(target_time+50,nrn));
				theSimulation.add_event(new xnet::pre_syn_event(target_time+100,nrn));
			}

			time += dt;
			theSimulation.run_until_empty();
		}
	}

	LOGGER(theSimulation.get_spikes().size());

	theSimulation.print_spikes(filename_base+"/xnet_pong_spikes.dat",timebase);
}
