#include "scan_engine.h"
#include "main.h"

static uint32_t scan_count = 0;

void scan_engine_init(void) {
    scan_count = 0;
}

void scan_cycle_run(void) {
	HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_0);
    scan_count++;

    // For now, just toggle the LED every 50 scans (500 ms total)
    // This proves the timer-driven scan cycle works
    if ((scan_count % 50) == 0) {
        HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
    }

    // Future: read_physical_inputs_to_image();
    // Future: execute_ladder_program();
    // Future: write_output_image_to_physical();
}

uint32_t scan_get_count(void) {
    return scan_count;
}
