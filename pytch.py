from microbit import display


def say(msg):
    display.scroll(msg, loop=True)
