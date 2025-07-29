import os
import sys


def is_frozen() -> bool:
    return getattr(sys, 'frozen', False)


def get_appdata_dir():
    if is_frozen():
        if sys.platform == "win32":
            base = os.getenv('APPDATA')
        elif sys.platform == "darwin":
            base = os.path.expanduser('~/Library/Application Support')
        else:
            base = os.getenv('XDG_CONFIG_HOME') or os.path.expanduser('~/.config')
        return os.path.join(base, 'UzDevid/Raya')

    return os.getcwd()


def appdata_path(relative_path):
    return os.path.join(get_appdata_dir(), relative_path)
