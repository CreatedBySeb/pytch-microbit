# Pytch (micro:bit)

[MicroPython](https://microbit-micropython.readthedocs.io/en/latest/)-based
firmware for the [micro:bit](https://microbit.org/) to allow it to be used with
[Pytch](https://pytch.org/).

## Firmware

The firmware hex files are built based on the `.py` MicroPython source files in
the root of the repository. The `pytch.py` file contains code that is common to
both major revisions of the micro:bit, and potentially future boards as well.
The `microbit_v1.py` and `microbit_v2.py` files are the entrypoints for their
respective major revisions, with the V1 code being a thin wrapper and the V2
code implementing the additional functionality on the board. While it is
possible to build a universal hex file compatible with both boards, the code
required to implement all of the V2 features runs into the limitations of the
V1 boards, so splitting them in this way is necessary.

### MicroPython Gotchas

There are some aspects of MicroPython that deviate from typical/standard Python
behaviour, with MicroPython for the V1 revision having more abnormalities. Some
of these are documented here:

- `type` objects do not have `__name__`, can re-create by parsing output of
    repr (V1 only)
- `bytes` does not have the `decode` method, use `str(b, "utf-8")` (V1 only)

## Scripts

This repository contains some Node.js scripts, based on the v20 'Iron' LTS
release, for creating the micro:bit hex files and flashing them. The source
for these is written in TypeScript in `src/`, and built to `dist/` using
`npm run build`. Shared code is located in `src/shared.ts`.

### `build.js`

This script takes no arguments and builds the hex files based on the
MicroPython code in the repository root using the `@microbit/microbit-fs`
package, similar to the micro:bit Python IDE. The output is placed in `build/`.

### `flash.js`

This script scans for micro:bit devices continuously and attempts to flash them
with the correct hex file using DAPLink via the `dapjs` package, similar to the
micro:bit Python IDE. Passing the `--once` flag only flashes the currently
connected devices rather than continuing to scan.
