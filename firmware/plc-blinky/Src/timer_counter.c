#include "timer_counter.h"
#include <string.h>

plc_timer_t   g_timers[PLC_TIMER_COUNT];
plc_counter_t g_counters[PLC_COUNTER_COUNT];

void timer_counter_init(void) {
    memset(g_timers,   0, sizeof(g_timers));
    memset(g_counters, 0, sizeof(g_counters));
}
