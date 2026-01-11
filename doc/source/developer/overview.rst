Overview
========

Pytch's support for the micro:bit uses the approach of turning the micro:bit
into a peripheral by loading specific software onto it, which is similar to the
`approach taken by Scratch <https://scratch.mit.edu/microbit>`_, but different
from the approach in MakeCode for micro:bit and the micro:bit Python Editor
where a specific program is prepared and loaded on to the device for standalone
execution. This approach was chosen due to the similar needs of Pytch to Scratch
based on their common concepts, and to minimise the amount of flashing required
to use the micro:bit from within Pytch.

The integration consists of three components, the MicroPython-based firmware
which runs on the device (in ``pytch-microbit``), the bridge code and UI in the
Pytch IDE (in ``pytch-webapp``), and the ``pytch.microbit`` Python library
provided for use in users' programs (in ``pytch-vm``). A simple protocol is used
for communication between the firmware and the Pytch IDE, which is described in
:doc:`protocol`.
