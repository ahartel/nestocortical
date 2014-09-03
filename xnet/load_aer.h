#pragma once

#include <tuple>
#include <vector>
#include <fstream>
#include <string>
#include <iostream>

using namespace std;

vector<tuple<unsigned int,unsigned int>> load_aer(string filename)
{
	std::ifstream file(filename, std::ios::binary);

	unsigned int a;
	unsigned int b;

	//vector<unsigned int> data;
	//vector<unsigned int> time;
	vector<tuple<unsigned int, unsigned int>> data_time;

	//for (int i=0; i<3; i++)
	while (file.read(reinterpret_cast<char*>(&a),2))
	{
		file.read(reinterpret_cast<char*>(&b),4);
		a = __builtin_bswap32(a)>>16;
		b = __builtin_bswap32(b)-3625530;
		//cout << hex << a << ", " << b << endl;
		//cout << dec << a << ", " << b << endl;
		//data.push_back(a);
		//time.push_back(b);
		data_time.push_back(make_tuple(a,b));
	}

	return data_time;
}
