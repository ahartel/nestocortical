#pragma once
#include <tuple>

typedef float Time_t;
typedef float Timeconst_t;
typedef unsigned int Id_t;
typedef unsigned char Weight_t;
typedef float Current_t;
typedef float Membrane_t;
typedef std::tuple<Time_t, Id_t> Spike_t;
struct ParamRange_t
{
	ParamRange_t(float f1, float f2) : range(std::make_tuple(f1,f2)) {}
	std::tuple<float, float> range;
};
struct NormalRange_t : public ParamRange_t
{
	NormalRange_t(float f1, float f2) : ParamRange_t(f1,f2) {}
	float mean() const { return std::get<0>(range);}
	float std() const { return std::get<1>(range);}
};

struct UniformRange_t : public ParamRange_t
{
	UniformRange_t(float f1, float f2) : ParamRange_t(f1,f2) {}
	float low() const { return std::get<0>(range);}
	float high() const { return std::get<1>(range);}
};
