from microbit import *
import os

BAUD = 115200
ENDL = "\n"
SEP = "|"
VER = "0.1"

_read_buf = ""


def var_buttons():
    return [button_a.is_pressed(), button_b.is_pressed()]


BASE_VARS = {
    "buttons": var_buttons,
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

    return [str(v) for v in handler()]


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
    uart.write(SEP.join(args) + ENDL)


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
    if button_a.was_pressed():
        send("button", ["a"])

    if button_b.was_pressed():
        send("button", ["b"])


def run(handlers=None, event_emitter=emit_events):
    _handlers = dict(BASE_HANDLERS)

    if handlers:
        _handlers.update(handlers)

    uart.init(BAUD)

    while True:
        cmd, args = read()
        handle_cmd(_handlers, cmd, args)
        event_emitter()
