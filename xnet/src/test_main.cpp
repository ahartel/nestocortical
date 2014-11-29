#include "load_aer.h"
#include <tuple>

using namespace std;

int main(int argc, char* argv[])
{
	auto data_time = load_aer(argv[1]);
	cout << get<0>(data_time).front() << endl;
	cout << get<1>(data_time).front() << endl;
	cout << get<0>(data_time).back() << endl;
	cout << get<1>(data_time).back() << endl;
}
