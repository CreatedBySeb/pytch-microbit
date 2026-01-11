Pytch micro:bit (developer guide)
=================================

The on-device software for the micro:bit is written using MicroPython and allows
for interfacing with the micro:bit like a peripheral over UART/serial. The
scripts for building and flashing the firmware are written in TypeScript and
leverage the ``@microbit/microbit-fs`` library used in the official Python
editor. Here we provide more information on how this is implemented and the
communication format.

.. toctree::
   :maxdepth: 1

   overview
   development
   protocol
