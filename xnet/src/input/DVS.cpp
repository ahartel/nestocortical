#include "DVS.h"
#include <iostream>

using namespace std;

	DVS::DVS(int image_width, int image_height) :
		previous_image(image_height,vector<bool>(image_width,false))
	{
		this->image_width = image_width;
		this->image_height = image_height;
	}

	vector<vector<int>> DVS::calculate_image_diff(vector<vector<bool>> const& image)
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

	vector<int> DVS::calculate_spikes(vector<vector<bool>> const& image)
	{
		// This is deliberate code copying from calculate_image_diff,
		// but I seriuosly don't want to iterate twice over the image space
		vector<int> spikes;
		vector<vector<int>> image_diff (image_height,vector<int>(image_width,0) );
		for (int y=0; y<image_height; ++y)
		{
			for (int x=0; x<image_width; ++x)
			{
				image_diff[y][x] = int(image[y][x]) - int(previous_image[y][x]);
				if (image_diff[y][x] > 0)
					spikes.push_back((y*image_height+x)*2);
				else if (image_diff[y][x] < 0)
					spikes.push_back((y*image_height+x)*2+1);
			}
		}

		//print_image_diff(image_diff);

		previous_image = image;
		return spikes;
	}

	void DVS::print_image_diff(vector<vector<int>> const& img)
	{
		for (int y=0; y<image_height; ++y)
		{
			for (int x=0; x<image_width; ++x)
			{
				cout << img[y][x] << " ";
			}
			cout << endl;
		}
	}
