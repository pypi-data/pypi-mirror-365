import errno
from functools import singledispatch
from typing import Never

from pyfuse3 import EntryAttributes, FUSEError


@singledispatch
def on_error(exc: Exception, *, errno_: int = 0) -> Never:
    """Log Exception and raise `FUSEError`"""
    # logger.exception(str(exc), exc_info=exc)
    raise FUSEError(errno_)


@on_error.register
def on_os_error(exc: OSError) -> Never:
    # logger.exception(str(exc), exc_info=exc)
    raise FUSEError(exc.errno)


@on_error.register
def on_key_error(exc: KeyError) -> Never:
    # logger.exception(str(exc), exc_info=exc)
    raise FUSEError(errno.ENOENT)


@on_error.register
def on_fuse_error(exc: FUSEError) -> Never:
    # logger.exception(str(exc), exc_info=exc)
    raise exc


@on_error.register
def on_is_a_dir_error(exc: IsADirectoryError) -> Never:
    # logger.exception(str(exc), exc_info=exc)
    raise FUSEError(exc.errno)


@on_error.register
def on_not_a_dir_error(exc: NotADirectoryError) -> Never:
    # logger.exception(str(exc), exc_info=exc)
    raise FUSEError(exc.errno)


@on_error.register
def on_file_not_found_error(exc: FileNotFoundError) -> Never:
    # logger.exception(str(exc), exc_info=exc)
    raise FUSEError(exc.errno)


def get_abstract_attrs(attr: EntryAttributes) -> str:
    return f"<EntryAttributes {attr.st_ino}::{attr.st_size}>"
