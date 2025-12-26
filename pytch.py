from microbit import *
import os

BAUD = 115200
ENDL = "\n"
SEP = "|"
PINS = (pin0, pin1, pin2)
VER = "0.1"

_gesture = ""
_pin_states = [0 for _ in PINS]
_read_buf = ""


def var_accel():
    return accelerometer.get_values()


def var_buttons():
    return [button_a.is_pressed(), button_b.is_pressed()]


def var_gesture():
    return [_gesture]


def var_light():
    return [display.read_light_level()]


def var_pins():
    return _pin_states


def var_temp():
    return [temperature()]


BASE_VARS = {
    "accel": var_accel,
    "buttons": var_buttons,
    "gesture": var_gesture,
    "light": var_light,
    "pins": var_pins,
    "temp": var_temp,
}


def cmd_hello(_):
    uname = os.uname()
    return ["microbit", uname.release, VER]


def cmd_var(args):
    if not args:
        raise TypeError("No variable name provided")

    name = args[0]
    handler = BASE_VARS.get(name)

    if not handler:
        raise ValueError("Unknown variable name '" + name + "'")

    return handler()


BASE_HANDLERS = {
    "hello": cmd_hello,
    "var": cmd_var,
}


def str_err(e):
    return repr(type(e)).split("'", 3)[1]


def read():
    global _read_buf

    while uart.any():
        message = uart.readline()

        if message:
            _read_buf += str(message, "utf-8")

        if _read_buf[-1] in (ENDL, "\r"):
            args = _read_buf.strip().split(SEP)
            _read_buf = ""
            command = args.pop(0)
            return command, args

    return None, []


def send(event, args):
    args.insert(0, event)
    uart.write(SEP.join(str(a) for a in args) + ENDL)


def handle_cmd(handlers, cmd, args):
    if not cmd:
        return

    handler = handlers.get(cmd)

    try:
        if not handler:
            raise TypeError("Unknown command '" + cmd + "'")

        results = handler(args) or []
    except Exception as e:
        send("err", [str_err(e), e.args[0]])
    else:
        send("ok", results)


def emit_events():
    global _gesture, _pin_states

    if button_a.was_pressed():
        send("button", ["a"])

    if button_b.was_pressed():
        send("button", ["b"])

    new_pins = [p.read_digital() for p in PINS]
    for i in range(0, len(PINS)):
        if new_pins[i] != _pin_states[i]:
            send("pin", [i, new_pins[i]])
            _pin_states[i] = new_pins[i]

    new_gesture = accelerometer.current_gesture()
    if new_gesture != _gesture and new_gesture:
        send("gesture", [new_gesture])
        _gesture = new_gesture


def run(handlers=None, event_emitter=emit_events):
    _handlers = dict(BASE_HANDLERS)

    if handlers:
        _handlers.update(handlers)

    uart.init(BAUD)

    while True:
        cmd, args = read()
        handle_cmd(_handlers, cmd, args)
        event_emitter()
