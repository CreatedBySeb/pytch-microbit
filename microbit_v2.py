from microbit import *
import pytch


def var_buttons():
    return [button_a.is_pressed(), button_b.is_pressed(), pin_logo.is_touched()]


def var_sound():
    return [microphone.sound_level()]


var_handlers = dict(pytch.BASE_VARS)
var_handlers.update(
    {
        "buttons": var_buttons,
        "sound": var_sound,
    }
)


def cmd_var(args):
    if not args:
        raise TypeError("No variable name provided")

    name = args[0]
    handler = var_handlers.get(name)

    if not handler:
        raise ValueError("Unknown variable name '" + name + "'")

    return [str(v) for v in handler()]


cmd_handlers = {
    "var": cmd_var,
}

pytch.run(cmd_handlers)
