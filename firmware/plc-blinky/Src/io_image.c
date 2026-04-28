#include "io_image.h"
#include "main.h"
#include <string.h>

// The global I/O image instance
plc_io_image_t g_io;

void io_image_init(void) {
    memset(&g_io, 0, sizeof(g_io));
}

void io_read_inputs(void) {
    // Industrial inputs I0..I7 via PC817 optocouplers (active-LOW)
    g_io.digital_in[0] = (HAL_GPIO_ReadPin(IND_IN_0_GPIO_Port, IND_IN_0_Pin) == GPIO_PIN_RESET);
    g_io.digital_in[1] = (HAL_GPIO_ReadPin(IND_IN_1_GPIO_Port, IND_IN_1_Pin) == GPIO_PIN_RESET);
    g_io.digital_in[2] = (HAL_GPIO_ReadPin(IND_IN_2_GPIO_Port, IND_IN_2_Pin) == GPIO_PIN_RESET);
    g_io.digital_in[3] = (HAL_GPIO_ReadPin(IND_IN_3_GPIO_Port, IND_IN_3_Pin) == GPIO_PIN_RESET);
    g_io.digital_in[4] = (HAL_GPIO_ReadPin(IND_IN_4_GPIO_Port, IND_IN_4_Pin) == GPIO_PIN_RESET);
    g_io.digital_in[5] = (HAL_GPIO_ReadPin(IND_IN_5_GPIO_Port, IND_IN_5_Pin) == GPIO_PIN_RESET);
    g_io.digital_in[6] = (HAL_GPIO_ReadPin(IND_IN_6_GPIO_Port, IND_IN_6_Pin) == GPIO_PIN_RESET);
    g_io.digital_in[7] = (HAL_GPIO_ReadPin(IND_IN_7_GPIO_Port, IND_IN_7_Pin) == GPIO_PIN_RESET);
}

void io_write_outputs(void) {
    // Industrial outputs Q0..Q3 via NPN transistor + relay module
    HAL_GPIO_WritePin(IND_OUT_0_GPIO_Port, IND_OUT_0_Pin,
                      g_io.digital_out[0] ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(IND_OUT_1_GPIO_Port, IND_OUT_1_Pin,
                      g_io.digital_out[1] ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(IND_OUT_2_GPIO_Port, IND_OUT_2_Pin,
                      g_io.digital_out[2] ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(IND_OUT_3_GPIO_Port, IND_OUT_3_Pin,
                      g_io.digital_out[3] ? GPIO_PIN_SET : GPIO_PIN_RESET);

    // Mirror Q0 to onboard LED (PC13 active-LOW) for visual feedback
    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13,
                      g_io.digital_out[0] ? GPIO_PIN_RESET : GPIO_PIN_SET);
}
