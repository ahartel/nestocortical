#pragma once

#include <tuple>
#include <vector>
#include <fstream>
#include <string>
#include <iostream>

#include "xnet_types.h"

using namespace std;

typedef vector<Spike_t> AERData;

void load_cache(string filename, AERData& data_time)
{

}

bool is_cached(string filename)
{
	return false;
}

void cache(string filename, AERData const& data_time)
{

}

vector<Spike_t> load_aer(string filename, int max_time=-1)
{
	std::ifstream file(filename, std::ios::binary);

	unsigned int a;
	unsigned int b;

	AERData data_time;

	if (!is_cached(filename))
	{
		while (file.read(reinterpret_cast<char*>(&a),2))
		{
			file.read(reinterpret_cast<char*>(&b),4);
			a = __builtin_bswap32(a)>>16;
			b = __builtin_bswap32(b)-3625530;

			if (max_time >= 0 && b>max_time)
				break;

			data_time.push_back(make_tuple(a,b));
		}
		cache(filename,data_time);
	}
	else
		load_cache(filename, data_time);


	return data_time;
}
