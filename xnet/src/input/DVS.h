#pragma once
#include <vector>

using namespace std;

class DVS
{
public:
	DVS(int image_width, int image_height);

	vector<vector<int>> calculate_image_diff(vector<vector<bool>> const& image);
	vector<int> calculate_spikes(vector<vector<bool>> const& image);

	void print_image_diff(vector<vector<int>> const& img);

private:
	vector<vector<bool>> previous_image;
	int image_width, image_height;

};
