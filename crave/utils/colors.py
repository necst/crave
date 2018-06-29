import sys


def color(text, color_code):
    if sys.platform == 'win32' and os.getenv('TERM') != 'xterm':
        return text

    return '\x1b[%dm%s\x1b[0m' % (color_code, text)


def red(text):
    return color(text, 31)


def green(text):
    return color(text, 32)


def yellow(text):
    return color(text, 33)


def blue(text):
    return color(text, 34)
