#include "ladder_vm.h"
#include "io_image.h"

#define VM_STACK_SIZE 16

// Read value at the given I/O address
static bool vm_read_addr(uint8_t addr) {
    if (addr <= 0x07) {
        return g_io.digital_in[addr];                      // I0..I7
    } else if (addr >= 0x10 && addr <= 0x17) {
        return g_io.digital_out[addr - ADDR_OUTPUT_BASE];  // Q0..Q7
    }
    return false;  // Invalid address — default to OFF
}

// Write value to the given I/O address
static void vm_write_addr(uint8_t addr, bool value) {
    if (addr >= 0x10 && addr <= 0x17) {
        g_io.digital_out[addr - ADDR_OUTPUT_BASE] = value;
    }
    // Writes to inputs or invalid addresses are silently ignored
}

vm_result_t ladder_vm_execute(const uint8_t *program, uint16_t program_len) {
    bool stack[VM_STACK_SIZE];
    int sp = -1;  // Stack pointer, -1 means empty

    uint16_t pc = 0;  // Program counter

    while (pc < program_len) {
        uint8_t opcode = program[pc++];

        // END instruction — stop execution
        if (opcode == OP_END) {
            return VM_OK;
        }

        // All other instructions have a 1-byte address operand
        if (pc >= program_len) {
            return VM_ERR_PROGRAM_TOO_LONG;  // Truncated program
        }
        uint8_t addr = program[pc++];

        bool value = vm_read_addr(addr);

        switch (opcode) {
            case OP_LD:
                if (sp + 1 >= VM_STACK_SIZE) return VM_ERR_STACK_OVERFLOW;
                stack[++sp] = value;
                break;

            case OP_LDN:
                if (sp + 1 >= VM_STACK_SIZE) return VM_ERR_STACK_OVERFLOW;
                stack[++sp] = !value;
                break;

            case OP_AND:
                if (sp >= 0) stack[sp] = stack[sp] && value;
                break;

            case OP_ANDN:
                if (sp >= 0) stack[sp] = stack[sp] && !value;
                break;

            case OP_OR:
                if (sp >= 0) stack[sp] = stack[sp] || value;
                break;

            case OP_ORN:
                if (sp >= 0) stack[sp] = stack[sp] || !value;
                break;

            case OP_OUT:
                if (sp >= 0) vm_write_addr(addr, stack[sp]);
                break;

            default:
                return VM_ERR_UNKNOWN_OPCODE;
        }
    }

    return VM_OK;  // Ran off the end without END — still OK
}
