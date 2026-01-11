Protocol
========

A simple protocol is used for communication with the micro:bit, with the
vertical bar (``|``) being used to separate values within a single message, and
a standard newline (``\n``) being used to separate messages.

A message can be one of two types:

1. **A command**: Sent from Pytch to the micro:bit in order to perform some
   action on the device (e.g. ``show_text|Hello\n``)
2. **An event**: Sent from the micro:bit to Pytch to inform it that some change
   has taken place which the user may have a hat block to act on (e.g.
   ``button|a\n``)

There are two special events, ``ok`` and ``err``, which indicate the result of
the last executed command. ``ok`` is followed by the return values of the
command, if there are any, and ``err`` is followed by the Python type of the
error and the error's first value, which is typically a string message
describing the error.

Most current commands do not return any values, with the exception of the
``hello`` and ``var`` commands as a special case. ``hello`` is used by Pytch to
verify the type, hardware version and software version of the device connected
during a handshake process. ``var`` is used to implement transparent variable
access from Pytch. For instance, rather than needing to call a function
``get_temperature()``, the user can access ``temperature`` as an attribute of
the micro:bit object, which feels more natural and more closely matches the
Scratch equivalent. Returning a value from a command is allowed by the protocol
and supported by the bridge code in the IDE, it is just not currently used
outside of these cases.


Message examples
----------------

Below are some examples of expected exchanges with the micro:bit, with newlines
explicitly included for clarity.

Successful ``hello`` command::

   hello\n
   ok|microbit|2.1.1|0.1\n

Successful ``pixel`` command::

   pixel|2|2|9\n
   ok\n

Failed ``pixel`` command::

   pixel|5|5|9\n
   err|ValueError|index out of bounds\n

A ``var`` call for the ``buttons`` variable::

   var|buttons\n
   ok|False|False|False\n


A ``button`` event::

   button|a\n
