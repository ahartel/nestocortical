#include <chrono>
#include <iomanip>
#include <iostream>

#ifdef COUT_ENABLED
using std::chrono::system_clock;
#define LOGGER(x) /*std::time_t tt = system_clock::to_time_t(system_clock::now());*/ std::cout << system_clock::to_time_t(system_clock::now()) << "\t" << x << std::endl
#else
// since comments cannot be inserted via macros, we'll do it this way:
#define LOGGER(x) do {} while(0)
#endif

