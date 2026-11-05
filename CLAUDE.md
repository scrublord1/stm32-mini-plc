# STM32 Mini PLC — notes for Claude

Custom miniature PLC on STM32F103C8T6 (Blue Pill). B.Tech major project, May 2026.

## Layout
- `firmware/plc-blinky/` — **the main PLC firmware** (STM32CubeIDE project, HAL). Despite the name, this is the real code.
- `firmware/modbus-master/` — separate STM32 test project acting as Modbus RTU master.
- `firmware/esp32-dashboard/` — ESP32 Arduino sketch, WiFi bridge / web dashboard.
- `tools/ladder_editor/editor.py` — Python (CustomTkinter) visual ladder editor + compiler + downloader.
- `tools/ladder_editor/Programs/*.json` — demo ladder programs.
- `docs/` — photos, videos, logic-analyzer captures. Don't read these unless asked.

## Firmware architecture (plc-blinky)
- `scan_engine.c` — scan cycle, driven by TIM2 (72 MHz / 7200 / 100 → 100 Hz, 10 ms).
- `io_image.c` — `g_io` process image: 8 DI, 8 DO, 2 AI (12-bit). Read inputs → execute → write outputs.
- `ladder_vm.c` — bytecode VM. Opcodes in `Inc/ladder_vm.h`:
  LD/LDN/AND/ANDN/OR/ORN (0x01–0x06), OUT 0x10, TON 0x20, CTU 0x21, LDT 0x22, LDC 0x23, LDEQ 0x24, RST 0x30, END 0xFF.
  Address map: I0–7 = 0x00–0x07, Q0–7 = 0x10–0x17, T0–7 = 0x20–0x27, C0–7 = 0x30–0x37.
- `timer_counter.c` — TON/CTU state.
- `eeprom.c` — AT24C64 (I2C1, 0x50, 8 KB, 32 B pages). 4 program slots × 2048 B with 4-byte header (magic 0xAA 0x55). Boot-slot config at 0x1FFC (magic 0xCC 0x33).
- `modbus.c` — RTU slave, address 0x01, FC01/FC03/FC05, 5 ms frame timeout, via MAX485.
- `oled_display.c` + `ssd1306.c` — 1.3" SH1106 OLED on I2C1 (shared bus with EEPROM).
- `uart_console.c` — serial console / program download.
- Peripherals: I2C1 @100 kHz, USART1 @115200, USART2 @9600, TIM2 interrupt.

## Rules when changing code
- **Opcode or address-map changes must be mirrored in `tools/ladder_editor/editor.py`** (the compiler). They're a matched pair.
- Keep the scan cycle deterministic: no blocking I2C/UART or `HAL_Delay` inside the scan path.
- Only edit inside `/* USER CODE BEGIN */ … /* USER CODE END */` in CubeMX-generated files (`main.c`, `stm32f1xx_it.c`, `stm32f1xx_hal_msp.c`), or regenerating from `.ioc` wipes changes.
- Never edit `Drivers/` (vendor HAL/CMSIS).
- EEPROM layout changes break saved programs — call it out explicitly.
- Target is Cortex-M3, 64 KB flash / 20 KB RAM: watch static buffers and stack.

## Building
STM32CubeIDE on Windows (no CLI build set up). Claude can't flash hardware; it can review, refactor and reason. Ask the user to build/flash and paste errors or UART output.

## Token hygiene
Skip `Drivers/`, `Debug/`, `.metadata/`, `.settings/`, `docs/`, and `ssd1306_fonts.c` unless the task needs them.
