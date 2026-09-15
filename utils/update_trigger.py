import os
import tempfile
import time

import utils.constants as constants
from utils.resources import resource_path


def trigger_path():
    return resource_path(constants.update_trigger_path, persistent=True)


def is_trigger_pending():
    return os.path.exists(trigger_path())


def write_trigger():
    """Atomically create/update the manual update trigger file."""
    path = trigger_path()
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)
    content = str(time.time())
    fd, temporary = tempfile.mkstemp(prefix="update_trigger.", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            file.write(content)
        os.replace(temporary, path)
    except OSError:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
    # bump mtime explicitly
    now = time.time()
    os.utime(path, (now, now))
    return path


def consume_trigger():
    """Delete the trigger file if present. Returns True if it was consumed."""
    path = trigger_path()
    try:
        os.remove(path)
        return True
    except FileNotFoundError:
        return False
    except OSError:
        return False
