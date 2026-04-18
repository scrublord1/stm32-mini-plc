#ifndef INC_IO_IMAGE_H_
#define INC_IO_IMAGE_H_

#include <stdint.h>
#include <stdbool.h>

// PLC I/O configuration — matches your project spec
#define PLC_DIGITAL_INPUT_COUNT   8
#define PLC_DIGITAL_OUTPUT_COUNT  8   // 4 relays + 4 transistor outputs
#define PLC_ANALOG_INPUT_COUNT    2

// I/O image — the "snapshot" that ladder logic operates on
typedef struct {
    bool     digital_in[PLC_DIGITAL_INPUT_COUNT];
    bool     digital_out[PLC_DIGITAL_OUTPUT_COUNT];
    uint16_t analog_in[PLC_ANALOG_INPUT_COUNT];   // 0-4095 for 12-bit ADC
} plc_io_image_t;

// Global I/O image — accessed by all modules
extern plc_io_image_t g_io;

// Functions
void io_image_init(void);
void io_read_inputs(void);    // Physical pins -> g_io.digital_in[]
void io_write_outputs(void);  // g_io.digital_out[] -> physical pins

#endif /* INC_IO_IMAGE_H_ */
