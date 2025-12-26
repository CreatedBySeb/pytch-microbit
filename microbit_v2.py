from microbit import *
import pytch

_logo_state = False
_sound = SoundEvent.QUIET


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


def emit_events():
    global _logo_state, _sound

    logo_state = pin_logo.is_touched()
    if logo_state != _logo_state:
        if logo_state:
            pytch.send("button", ["logo"])

        _logo_state = logo_state

    new_sound = microphone.current_event()
    if new_sound != _sound:
        pytch.send("sound", ["loud" if new_sound == SoundEvent.LOUD else "quiet"])
        _sound = new_sound

    pytch.emit_events()


pytch.run(cmd_handlers, emit_events)
