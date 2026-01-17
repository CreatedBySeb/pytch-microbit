Development
===========

The micro:bit software is currently developed in the ``pytch-microbit``
repository. The MicroPython source exists in the root of the repository, with
``pytch.py`` containing the code common to both major board revisions (V1 and
V2), while device-specific code is contained in ``microbit_v1.py`` or
``microbit_v2.py`` respectively, which is renamed to ``main.py`` in the HEX file
in order to become the entrypoint on boot. The reference for the micro:bit
version of MicroPython is available
`here <https://microbit-micropython.readthedocs.io/en/latest/>`_.

The scripts which build the software and enable rapid flashing are located in
the ``src`` directory and written in TypeScript. The ``build`` script leverages
the official ``@microbit/microbit-fs`` library to prepare the HEX file, also
used by the official micro:bit Python Editor. The ``flash`` script uses
``dap.js`` for flashing, just like the implementation in the Pytch IDE.

For the V1 micro:bit, the amount of memory available (16KB) is a significant
constraint, as the code has to be parsed by the MicroPython interpreter on boot
and compiled into bytecode. The V2 micro:bit has significantly more memory
(128KB or 8 times more), and so this is much less of a concern. This is why the
code in ``pytch.py`` is written more compactly, as it has to be simple enough to
be parsable on V1 boards.

**The V1 version of the firmware is less well tested than V2 and may encounter
instability due to the lower memory size, it should be considered a work in
progress.**


Building and flashing
---------------------

The ``build`` script takes no arguments, and can be invoked using either
``node dist/build.js`` or ``npm run build:hex`` after building the scripts with
``npm run build:scripts``. You can also build both the scripts and HEX files
with just ``npm run build``. The output is placed in the ``build/`` directory.

The ``flash`` script takes an optional ``--once`` argument, and can only be
invoked directly using ``node dist/flash.js`` after building the scripts with
``npm run build:scripts``. It expects that HEX files have already been built by
the ``build`` script and are located in a ``build/`` directory relative to the
current working directory. By default, the ``flash`` script will stay running
indefinitely and will flash any micro:bit devices connected with the correct
firmware, V1 or V2, unless it has already seen their serial number in the
current session, enabling it to be used effectively for bulk flashing. If
the ``--once`` argument was supplied, it will only flash the micro:bit devices
currently connected when the program is run, and then exit.

When working on the firmware, running::

   node dist/build.js && node dist/flash.js --once

will build and then immediately flash the firmware to the connected device,
assuming that it is not already in use by Pytch. If it is, you will need to
disconnect it in Pytch first to be able to flash it, as both use the same
DAPLink interface.


Manual testing
--------------

You can use a tool like ``screen`` or ``minicom`` to connect to the micro:bit
directly for testing. Before plugging in your micro:bit, run ``ls /dev/ttyACM*``
on Linux or ``ls /dev/cu.*`` on macOS to determine the devices already
connected, then run the command again after connecting the micro:bit to
determine the correct device path. (Usually ``/dev/ttyACM0`` on Linux if you
don't have another serial device connected.) Then use one of the following
commands, replacing ``$DEVICE`` with the identified path::

   screen $DEVICE 115200
   minicom -b 115200 -D $DEVICE

You can then type commands in manually and execute them by hitting return/enter.
You should also see any events that are sent by the micro:bit in response to
interacting with the device. You won't be able to see what you are typing, since
the firmware does not echo the input back. You can also use CTRL+C to exit the
program and return to the MicroPython REPL, which can be used for testing
snippets during development, and then use CTRL+D to reset back to the firmware.

If using ``minicom``, adding the following to your ``~/.minirc.dfl`` file is
recommended to handle the fact that the firmware does not use carriage returns
(space sensitive)::

   pu addcarreturn    Yes

``screen`` does not have an equivalent setting and so will display each event
inset from the last, as ``minicom`` does without this setting, so ``minicom``
with this setting is recommended.


Build process
-------------

The ``build`` script works by performing the following steps:

1. Read in the MicroPython source files
2. Retrieve the latest MicroPython release for each board revision
3. Combine the base MicroPython HEX file and the MicroPython source into a
   separate HEX file for each revision
4. Write the HEX files out to the ``build/`` directory as
   ``pytch-microbit-v{REV}.hex``, where ``{REV}`` is the board major revision

This ensures that the HEX files are always built with the latest available
version of MicroPython for the board as of the build time.

The repositories for the different board revisions are:

* **V1**: `bbcmicrobit/micropython <https://github.com/bbcmicrobit/micropython/>`_
* **V2**: `microbit-foundation/micropython-microbit-v2 <https://github.com/microbit-foundation/micropython-microbit-v2>`_


MicroPython limitations
-----------------------

MicroPython is not fully compatible with CPython, and some significant
limitations exist, especially on the latest version available for the V1
micro:bit boards. Some relevant limitations are listed here, along with a
workaround. If a limitation only applies to one revision, it is placed in square
brackets (``[]``) at the beginning.

* [V1] ``type`` objects do not have ``__name__``, can be re-created by parsing
  the output of ``repr``
* [V1] ``bytes`` objects do not have the ``decode`` method, use
  ``str(b, "utf-8")`` instead
* [V1] Sometimes ``microbit.accelerometer.current_gesture()`` returns ``''``,
  do a truthy check before using the value
