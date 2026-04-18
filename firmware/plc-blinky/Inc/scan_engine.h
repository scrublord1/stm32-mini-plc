#ifndef INC_SCAN_ENGINE_H_
#define INC_SCAN_ENGINE_H_

#include <stdint.h>

void scan_engine_init(void);
void scan_cycle_run(void);
uint32_t scan_get_count(void);

#endif /* INC_SCAN_ENGINE_H_ */
