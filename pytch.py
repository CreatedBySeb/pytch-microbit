from microbit import *
import os

BAUD = 115200
ENDL = "\n"
SEP = "|"
PINS = (pin0, pin1, pin2)
VER = "0.1"

_gesture = ""
_pin_states = [0, 0, 0]
_read_buf = ""


BASE_VARS = {
    "accel": lambda: list(accelerometer.get_values()),
    "buttons": lambda: [button_a.is_pressed(), button_b.is_pressed()],
    "gesture": lambda: [_gesture],
    "light": lambda: [display.read_light_level()],
    "pins": lambda: _pin_states,
    "temp": lambda: [temperature()],
}


def cmd_clear(_):
    display.show("", loop=False)
    display.clear()


def cmd_hello(_):
    uname = os.uname()
    return ["microbit", uname.release, VER]


def cmd_pixel(args):
    if len(args) < 3:
        args.push(9)

    display.set_pixel(*[int(a) for a in args])


def cmd_scroll(args):
    wait = len(args) > 1 and args[1] == "True"
    loop = len(args) > 2 and args[2] == "True"
    display.scroll(args[0], wait=wait, loop=loop)


def cmd_show_img(args):
    if hasattr(Image, args[0]):
        img = getattr(Image, args[0])
    else:
        img = Image(args[0])

    display.show(img)


def cmd_show_text(args):
    wait = len(args) > 1 and args[1] == "True"
    loop = len(args) > 2 and args[2] == "True"
    display.show(args[0], wait=wait, loop=loop)


def cmd_var(args):
    name = args[0]
    handler = BASE_VARS.get(name)

    if not handler:
        raise ValueError("Unknown variable name '" + name + "'")

    return handler()


def cmd_write_d(args):
    PINS[int(args[0])].write_digital(int(args[1]))


BASE_HANDLERS = {
    "clear": cmd_clear,
    "hello": cmd_hello,
    "pixel": cmd_pixel,
    "reset": cmd_clear,
    "scroll": cmd_scroll,
    "show_img": cmd_show_img,
    "show_text": cmd_show_text,
    "var": cmd_var,
    "write_d": cmd_write_d,
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

    for i in range(0, len(PINS)):
        try:
            val = PINS[i].read_digital()
        except ValueError:
            if i != 0:
                raise
            continue

        if val != _pin_states[i]:
            send("pin", [i, val])
            _pin_states[i] = val

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
