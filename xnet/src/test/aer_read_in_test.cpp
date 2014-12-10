#include "load_aer.h"
#include <gtest/gtest.h>
#include <tuple>

using namespace std;

string filename;

TEST(AER_DATA,READ)
{
	auto data_time = load_aer(filename);
	EXPECT_EQ(get<0>(data_time.front()),24352);
	EXPECT_EQ(get<1>(data_time.front()),221429230);
	EXPECT_EQ(get<0>(data_time.back()),25130);
	EXPECT_EQ(get<1>(data_time.back()),266243170);
}


int main(int argc, char** argv) {
	filename = argv[1];
	::testing::InitGoogleTest(&argc, argv);
	::testing::FLAGS_gtest_death_test_style = "fast";
	return RUN_ALL_TESTS();
}
