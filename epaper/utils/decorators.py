from functools import wraps, partial
import logging

from epaper.data.file_descriptors import count_open_fds, get_fds_from_proc_fs

logger = logging.getLogger(__name__)


def compare_before_after(f, cmp_fn):
    @wraps(f)
    def wrapper(*args, **kwargs):
        before = cmp_fn()
        ret = f(*args, **kwargs)
        after = cmp_fn()
        match (before, after):
            case (int(), int()) | (float(), float()):
                diff = after - before
            case (set(), set()):
                diff = after - before
            case (dict(), dict()):
                diff = {k: after[k] for k in after if k not in before}
            case _:
                if before == after:
                    diff = None
                else:
                    diff = "NOIMPL"
        if diff:
            logger.debug(
                f"{f.__name__} - using cmp_fn {cmp_fn.__name__} - {before=} {after=} {diff=}"
            )
        else:
            logger.debug(
                f"{f.__name__} - using cmp_fn {cmp_fn.__name__} - NODIFF - {after}"
            )
        return ret

    return wrapper


fds_before_after = partial(compare_before_after, cmp_fn=get_fds_from_proc_fs)
