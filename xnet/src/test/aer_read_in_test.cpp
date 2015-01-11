#include "load_aer.h"
#include <gtest/gtest.h>
#include <tuple>

using namespace std;

string filename;

TEST(AER_DATA,READ)
{
	auto data_time = load_aer(filename);
	float first_spike_time = get<1>(data_time.front());
	float last_spike_time = get<1>(data_time.back());

	EXPECT_EQ(get<0>(data_time.front()),24352);
	EXPECT_EQ(first_spike_time,221429230);
	EXPECT_EQ(get<0>(data_time.back()),25130);
	EXPECT_EQ(last_spike_time,266243170);

	unsigned int last_time = 0;
	unsigned int this_time = 0;
	unsigned int delta_t = 100;
	for (auto spike : data_time)
	{
		this_time = get<0>(spike);
		if (this_time-last_time>0 && this_time - last_time < delta_t)
			delta_t = this_time-last_time;
		last_time = this_time;
	}
	cout << delta_t << endl;
	cout << data_time.size() << " in " << (last_spike_time-first_spike_time)/1.0e6 << " seconds" << endl;
	cout << "average spike rate: " << float(data_time.size())/(last_spike_time-first_spike_time) << " Hz" << endl;
}


int main(int argc, char** argv) {
	filename = argv[1];
	::testing::InitGoogleTest(&argc, argv);
	::testing::FLAGS_gtest_death_test_style = "fast";
	return RUN_ALL_TESTS();
}
