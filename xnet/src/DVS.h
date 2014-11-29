#pragma once
#include <vector>

class DVS
{
private:
	vector<vector<bool>> previous_image;
	int image_width, image_height;

public:
	DVS(int image_width, int image_height) : previous_image(image_height,vector<bool>(image_width,false))
	{
		this->image_width = image_width;
		this->image_height = image_height;
	}

	vector<vector<int>> calculate_spikes(vector<vector<bool>> image)
	{
		vector<vector<int>> image_diff (image_height,vector<int>(image_width,0) );
		for (int x=0; x<image_width; ++x)
		{
			for (int y=0; y<image_height; ++y)
			{
				image_diff[y][x] = int(image[y][x]) - int(previous_image[y][x]);
			}
		}
		previous_image = image;
		return image_diff;
	}
};
