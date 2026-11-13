# Hardware, FPGA and HDL artifacts

Use for bitstreams, Verilog/VHDL, simulation dumps, logic-analyzer captures, firmware images, JTAG/UART and custom boards.

## Identify the artifact

- Bitstream vendor/format (Xilinx `.bit`, Intel `.sof/.rbf`, Lattice, openFPGALoader).
- HDL source, testbench, constraints and generated netlist.
- VCD/FST/SAIF waveform, logic-analyzer export, Saleae/DSLogic capture.
- Firmware container (UBI, squashfs, JFFS2, vendor header), CPU architecture and boot chain.
- Board clues: silkscreen, datasheet, pinout, clock, boot mode, debug header.

Do not assume an FPGA bitstream can be decompiled like software; first look for supplied HDL, a simulation model or a documented register map.

## Recover the logic

1. Read the top-level HDL/testbench and identify inputs, outputs, clock/reset and state.
2. If only a bitstream is supplied, look for a matching vendor tool/project file or a known open bitstream format; otherwise treat it as a black box and use the board interface.
3. Reconstruct the data path: shift registers, LFSRs, counters, S-boxes, FSMs.
4. Simulate with `iverilog`/`verilator` and compare against supplied vectors.
5. For a waveform, decode the protocol from transitions; verify bit order, clock edge and framing.

## Firmware and debug

- Carve the filesystem, identify the CPU, and locate the entry point.
- Check UART/JTAG pins and baud rates from the board/challenge; do not brute-force unknown hardware.
- Emulate the firmware with QEMU/Unicorn when the architecture and peripherals are modeled.
- Recover keys from secure boot/OTP only if the challenge explicitly provides the device or dump.

## Common traps

- Wrong clock polarity/edge or bit order.
- Bitstream endianness/byte-swap.
- HDL simulation ignoring reset or initial state.
- Waveform decimated below the signal bandwidth.
- Firmware compressed/encrypted with a header key stored elsewhere.

## Verify

Round-trip a supplied vector through your model, or reproduce a known output from the HDL/firmware. Report the toolchain/version and the exact signal mapping. Do not claim a bitstream was fully reverse engineered when only the interface was modeled.
