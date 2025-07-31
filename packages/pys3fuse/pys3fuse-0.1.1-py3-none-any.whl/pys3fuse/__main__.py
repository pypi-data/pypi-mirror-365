import asyncio
import logging
from argparse import ArgumentParser

import pyfuse3

from .log_config import (
    file_queue_listener,
    pys3fuse_logger as logger,
    queue_listener,
)
from .passthrough import PassThroughFS


def main():
    queue_listener.start()
    file_queue_listener.start()

    parser = ArgumentParser("PyS3FUSE")

    parser.add_argument(
        "source",
        type=str,
        help="Directory tree to mirror",
    )
    parser.add_argument(
        "mountpoint",
        type=str,
        help="Where to mount the file system",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debugging output",
    )

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    logger.debug("Mounting...")
    operations = PassThroughFS(args.source)
    fuse_options = set(pyfuse3.default_options)
    fuse_options.add(f"fsname={PassThroughFS.__name__}")

    pyfuse3.init(operations, args.mountpoint, fuse_options)

    try:
        logger.debug("Entering mainloop...")
        asyncio.run(pyfuse3.main())
    except KeyboardInterrupt:
        logger.debug("Unmounting...")
        pyfuse3.close(unmount=True)
    finally:
        queue_listener.stop()
        file_queue_listener.stop()


if __name__ == "__main__":
    main()
