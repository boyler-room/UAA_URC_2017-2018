#define TARGET 3

#define TARGET_ACTUATOR 1
#define TARGET_STEPPER 2
#define TARGET_SENSOR 3

#ifdef TARGET

#if TARGET==TARGET_ACTUATOR
#include "actuator.h"

#elif TARGET==TARGET_STEPPER
#include "stepper.h"

#elif TARGET==TARGET_SENSOR
#include "sensor.h"

#else
#error Invalid Target!

#endif

#else
#error No Target Specified!

#endif
