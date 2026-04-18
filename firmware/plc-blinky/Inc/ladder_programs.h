#ifndef INC_LADDER_PROGRAMS_H_
#define INC_LADDER_PROGRAMS_H_

#include <stdint.h>
#include "ladder_vm.h"

// Motor start/stop with seal-in:
//   LD   I0   ; Load Start button
//   OR   Q0   ; OR with Motor (seal-in)
//   ANDN I1   ; AND NOT Stop button
//   OUT  Q0   ; Write to Motor output
//   END
static const uint8_t motor_start_stop_program[] = {
    OP_LD,   0x00,
    OP_OR,   0x10,
    OP_ANDN, 0x01,
    OP_OUT,  0x10,
    OP_END
};

#define MOTOR_PROGRAM_LEN  (sizeof(motor_start_stop_program))
// NOT gate: Motor = NOT Start
/*static const uint8_t not_gate_program[] = {
    OP_LDN, 0x00,
    OP_OUT, 0x10,
    OP_END
};

#define NOT_GATE_PROGRAM_LEN  (sizeof(not_gate_program)) */
#endif /* INC_LADDER_PROGRAMS_H_ */
