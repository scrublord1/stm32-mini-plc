#ifndef INC_TIMER_COUNTER_H_
#define INC_TIMER_COUNTER_H_

#include <stdint.h>
#include <stdbool.h>

#define PLC_TIMER_COUNT   8
#define PLC_COUNTER_COUNT 8

// Timer state
typedef struct {
    uint32_t elapsed_ms;    // Milliseconds elapsed since last rising edge
    bool     output;        // Timer output (Q)
    bool     prev_input;    // Previous input state (for edge detection)
} plc_timer_t;

// Counter state
typedef struct {
    uint16_t count;         // Current count value
    bool     output;        // Counter output (Q)
    bool     prev_input;    // Previous input state (for edge detection)
} plc_counter_t;

// Global instances
extern plc_timer_t   g_timers[PLC_TIMER_COUNT];
extern plc_counter_t g_counters[PLC_COUNTER_COUNT];

void timer_counter_init(void);

#endif
