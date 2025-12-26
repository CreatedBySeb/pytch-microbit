from microbit import *
import music
import os

BAUD = 115200
BR_RANGE = range(9)
ENDL = "\n"
SEP = "|"
PINS = (pin0, pin1, pin2)
PIX_RANGE = range(5)
VER = "0.1"

_gesture = ""
_pin_states = [0 for _ in PINS]
_read_buf = ""


def wait_loop(args):
    wait = len(args) > 1 and args[1] == "True"
    loop = len(args) > 2 and args[2] == "True"
    return wait, loop


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


def cmd_play_music(args):
    wait, loop = wait_loop(args)

    if hasattr(music, args[0]):
        song = getattr(music, args[0])
    else:
        song = args[0]

    music.play(song, wait=wait, loop=loop)


def cmd_scroll(args):
    wait, loop = wait_loop(args)
    display.scroll(args[0], wait=wait, loop=loop)


def cmd_show_img(args):
    if hasattr(Image, args[0]):
        img = getattr(Image, args[0])
    else:
        img = Image(args[0])

    display.show(img)


def cmd_show_text(args):
    wait, loop = wait_loop(args)
    display.show(args[0], wait=wait, loop=loop)


def cmd_stop_music(_):
    music.stop()


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
    "play_music": cmd_play_music,
    "scroll": cmd_scroll,
    "show_img": cmd_show_img,
    "show_text": cmd_show_text,
    "stop_music": cmd_stop_music,
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
