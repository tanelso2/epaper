import logging
import os

logger = logging.getLogger(__name__)


def get_fds_from_proc_fs() -> dict[str, str]:
    self_fds_dir = "/proc/self/fd"
    ret = {}
    for fd in os.listdir(self_fds_dir):
        try:
            target = os.readlink(os.path.join(self_fds_dir, fd))
            ret[fd] = target
        except OSError:
            pass
    return ret


def count_open_fds() -> int:
    return len(get_fds_from_proc_fs())
