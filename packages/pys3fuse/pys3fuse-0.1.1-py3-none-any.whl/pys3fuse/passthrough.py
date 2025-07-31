import os
import stat as stat_m
from collections import defaultdict
from os import fsdecode, fsencode, stat_result
from pathlib import Path
from typing import Optional, Sequence, Tuple, cast

import pyfuse3.asyncio
from pyfuse3 import (
    EntryAttributes,
    FUSEError,
    FileHandleT,
    FileInfo,
    FileNameT,
    FlagT,
    InodeT,
    ModeT,
    Operations,
    ReaddirToken,
    RequestContext,
    SetattrFields,
    StatvfsData,
)

from .log_config import pys3fuse_logger as logger
from .utils import on_error

pyfuse3.asyncio.enable()


class PassThroughFS(Operations):
    enable_writeback_cache = True

    def __init__(self, source: Path):
        super().__init__()
        self._inode_path_map: dict[InodeT, Path | set[Path]] = {
            pyfuse3.ROOT_INODE: source
        }
        self._lookup_cnt = defaultdict(lambda: 0)
        self._fd_inode_map = {}
        self._inode_fd_map = {}
        self._fd_open_count = {}

    def _inode_to_path(self, inode: InodeT) -> Path:
        """Return the path for the inode"""
        try:
            val = self._inode_path_map[inode]
        except KeyError as exc:
            on_error(exc)

        if isinstance(val, set):
            # In case of hardlinks, pick any path
            val = next(iter(val))
        return Path(val)

    def _add_path(self, inode: InodeT, path: Path) -> None:
        """Add a path to inode path map

        Adds the hardlink paths to a set for the inode
        Increments the lookup cnt for the inode by one
        """
        self._lookup_cnt[inode] += 1

        # With hardlinks, one inode may map to multiple paths.
        if inode not in self._inode_path_map:
            self._inode_path_map[inode] = path
            return

        val = self._inode_path_map[inode]
        if isinstance(val, set):
            val.add(path)
        elif val != path:
            self._inode_path_map[inode] = {path, val}

    def _forget_path(self, inode: int | InodeT, path: Path):
        logger.debug(f"_forget_path {path=}/{inode=}")
        val = self._inode_path_map[inode]
        if isinstance(val, set):
            val.remove(path)
            if len(val) == 1:
                self._inode_path_map[inode] = next(iter(val))
        else:
            del self._inode_path_map[inode]

    @staticmethod
    def _entry_from_stat_result(stat_res: stat_result) -> EntryAttributes:
        entry = EntryAttributes()

        entry.st_ino = cast(InodeT, stat_res.st_ino)
        entry.generation = 0
        entry.entry_timeout = 0
        entry.attr_timeout = 0
        entry.st_mode = cast(ModeT, stat_res.st_mode)
        entry.st_nlink = stat_res.st_nlink
        entry.st_uid = stat_res.st_uid
        entry.st_gid = stat_res.st_gid
        entry.st_size = stat_res.st_size
        entry.st_blksize = stat_res.st_blksize
        entry.st_blocks = stat_res.st_blocks
        entry.st_atime_ns = stat_res.st_atime_ns
        entry.st_ctime_ns = stat_res.st_ctime_ns
        entry.st_mtime_ns = stat_res.st_mtime_ns

        return entry

    async def forget(self, inode_list: Sequence[Tuple[InodeT, int]]) -> None:
        """Decrease lookup counts for inodes in inode_list

        :raises FUSEError if the inode in inode_list is not found
        """
        logger.debug(f"{inode_list=}")
        for inode, nlookup in inode_list:
            if self._lookup_cnt[inode] > nlookup:
                self._lookup_cnt[inode] -= 1
                continue
            assert inode not in self._inode_fd_map
            del self._lookup_cnt[inode]
            try:
                del self._inode_path_map[inode]
            except KeyError:
                pass

    async def lookup(
        self,
        parent_inode: InodeT,
        name: FileNameT,
        ctx: RequestContext,
    ) -> EntryAttributes:
        """Look up a directory entry by name and get its attributes.

        This method should return an EntryAttributes instance
        for the directory entry name in the directory with
        inode parent_inode.

        :raises FUSEError if the parent_inode is not found
        """
        name = fsdecode(name)
        directory = self._inode_to_path(parent_inode)

        path = directory / name
        attr = self.lstat(path)
        if name != "." and name != "..":
            self._add_path(attr.st_ino, path)
        return attr

    async def getattr(self, inode: InodeT, ctx: RequestContext) -> EntryAttributes:
        """Getattr of the inode

        :raises FUSEError if the inode is not found
        """
        if inode in self._inode_fd_map:
            return self.fstat(self._inode_fd_map[inode])
        return self.lstat(self._inode_to_path(inode))

    def fstat(self, fd: int) -> EntryAttributes:
        """Perform os.fstat on fd and return `EntryAttributes`"""
        try:
            stat = os.fstat(fd)
        except OSError as exc:
            on_error(exc)

        entry = self._entry_from_stat_result(stat)
        return entry

    def lstat(self, path: Path) -> EntryAttributes:
        """Perform os.lstat on path and return `EntryAttributes`"""
        try:
            stat = os.lstat(path)
        except OSError as exc:
            on_error(exc)

        entry = self._entry_from_stat_result(stat)
        return entry

    async def readlink(self, inode: InodeT, ctx: RequestContext) -> FileNameT:
        """Return target of symbolic link inode.

        :raises FUSEError if the inode is not found
        :raises FUSEError if os.readlink cause error
        """
        path = self._inode_to_path(inode)
        logger.debug(f"{path=}")
        try:
            target = os.readlink(path)
        except OSError as exc:
            on_error(exc)
        return FileNameT(fsencode(target))

    async def opendir(self, inode: InodeT, ctx: RequestContext) -> FileHandleT:
        """Open the directory with inode.

        This method should return an integer file handle.

        The file handle will be passed to the `readdir, fsyncdir and releasedir`
        methods to identify the directory.

        :raises FUSEError if the inode is not found
        """
        logger.debug(f"{inode=}")
        return FileHandleT(inode)

    async def readdir(
        self, fh: FileHandleT, start_id: int, token: ReaddirToken
    ) -> None:
        """Read entries in open directory fh.

        This method should list the contents of directory fh
        (as returned by a prior opendir call),
        starting at the entry identified by start_id.

        :raises FUSEError if the fh is not found
        """
        directory = self._inode_to_path((InodeT(fh)))
        logger.debug(f"{directory=}")
        entries = []
        for dir_entry in os.scandir(directory):
            if dir_entry.name in [".", ".."]:
                continue
            attr = self._entry_from_stat_result(dir_entry.stat())
            entries.append((attr.st_ino, dir_entry.name, attr, dir_entry.path))

        logger.debug(f"Read #{len(entries)} entries from {directory=}")

        # This is not fully posix compatible. If there are hardlinks
        # (two names with the same inode), we don't have a unique
        # offset to start in between them. Note that we cannot simply
        # count entries, because then we would skip over entries
        # (or return them more than once) if the number of directory
        # entries changes between two calls to readdir().
        for inode, name, attr, path in sorted(entries):
            if inode <= start_id:
                continue
            if not pyfuse3.readdir_reply(token, FileNameT(fsencode(name)), attr, inode):
                break
            self._add_path(inode, Path(path))

    async def unlink(
        self, parent_inode: InodeT, name: FileNameT, ctx: RequestContext
    ) -> None:
        """Remove a (possibly special) file.

        This method must remove the (special or regular) file
        name from the directory with inode parent_inode.
        """
        name = fsdecode(name)
        logger.debug(f"{parent_inode=}//{name=}")
        parent = self._inode_to_path(parent_inode)
        path = parent / name

        try:
            inode = os.lstat(path).st_ino
            os.unlink(path)
        except FileNotFoundError as exc:
            on_error(exc)
        except OSError as exc:
            on_error(exc)
        if inode is self._lookup_cnt:
            self._forget_path(inode, path)

    async def rmdir(
        self, parent_inode: InodeT, name: FileNameT, ctx: RequestContext
    ) -> None:
        """Remove a directory

        This method must remove the directory name from the directory with inode parent_inode.
        If there are still entries in the directory, the method should raise FUSEError(errno.ENOTEMPTY).

        :raises FUSEError if parent does not exist
        """
        name = fsdecode(name)
        logger.debug(f"{parent_inode=}//{name=}")
        parent = self._inode_to_path(parent_inode)
        path = parent / name

        try:
            inode = os.lstat(path).st_ino
            os.rmdir(path)
        except FileNotFoundError as exc:
            on_error(exc)
        except OSError as exc:
            raise FUSEError(exc.errno)

        if inode in self._lookup_cnt:
            self._forget_path(inode, path)

    async def symlink(
        self,
        parent_inode: InodeT,
        name: FileNameT,
        target: FileNameT,
        ctx: RequestContext,
    ) -> EntryAttributes:
        """Create a symbolic link.

        This method must create a symlink link named name
        in the directory with inode parent_inode, pointing to target.

        :raises FUSEError if parent_inode is not found.
        """
        name = fsdecode(name)
        target = fsdecode(target)
        logger.debug(f"{parent_inode=}//{name} -> {target=}")

        parent = self._inode_to_path(parent_inode)
        path = parent / name
        try:
            os.symlink(target, path)
            os.chown(path, ctx.uid, ctx.gid, follow_symlinks=False)
        except OSError as exc:
            on_error(exc)

        stat = self.lstat(path)
        self._add_path(stat.st_ino, path)
        return stat

    async def rename(
        self,
        p_inode_old: InodeT,
        name_old: str,
        p_inode_new: InodeT,
        name_new: str,
        flags: FlagT,
        ctx: RequestContext,
    ) -> None:
        """Rename a directory entry

        This method must rename name_old in the directory with
        inode parent_inode_old to name_new in the directory
        with inode parent_inode_new.

        If name_new already exists, it should be overwritten.

        os.rename behaviour
         * On Unix, if src is a file and dst is a directory or vice versa,
           an IsADirectoryError or a NotADirectoryError will be raised respectively.

         * If both are directories and dst is empty, dst will be silently replaced.

         * If dst is a non-empty directory, an OSError is raised.

         * If both are files, dst will be replaced silently if the user has permission.

         * The operation may fail on some Unix flavors if src and dst are on different filesystems.

         * If successful, the renaming will be an atomic operation (this is a POSIX requirement).

        :raises FUSEError if parent_inode_old(new) does not exist
        """
        name_old = fsdecode(name_old)
        name_new = fsdecode(name_new)
        logger.debug(f"{p_inode_old=}//{name_old=} -> {p_inode_new=}//{name_new=}")
        parent_old = self._inode_to_path(p_inode_old)
        parent_new = self._inode_to_path(p_inode_new)

        path_old = parent_old / name_old
        path_new = parent_new / name_new

        try:
            os.rename(path_old, path_new)
            inode = self.lstat(path_new).st_ino
        except IsADirectoryError as exc:
            # if src is file and dst is a directory
            on_error(exc)
        except NotADirectoryError as exc:
            # if src is directory and dst is a file
            on_error(exc)
        except OSError as exc:
            on_error(exc)

        # Let the inode associated with name_old in parent_inode_old be inode_moved,
        # and the inode associated with name_new in parent_inode_new (if it exists)
        # be called inode_deref.
        # If inode_deref exists and has a non-zero lookup count,
        # or if there are other directory entries referring to inode_deref,
        # the file system must update only the directory entry for name_new
        # to point to inode_moved instead of inode_deref.
        #
        # (Potential) removal of inode_deref (containing the previous contents of name_new)
        # must be deferred to the forget method to be carried out
        # when the lookup count reaches zero
        # (and of course only if at that point there are no more directory entries
        # associated with inode_deref either).
        if inode not in self._lookup_cnt:
            return

        path = self._inode_path_map[inode]
        if isinstance(path, set):
            assert len(path) > 1, "raised in rename"
            path.add(path_new)
            path.remove(path_old)
        else:
            assert path == path_old, "raised in rename"
            self._inode_path_map[inode] = path_new

    async def link(
        self,
        inode: InodeT,
        new_parent_inode: InodeT,
        new_name: FileNameT,
        ctx: RequestContext,
    ) -> EntryAttributes:
        """Create directory entry name in parent_inode referring to inode.

        In other words: Create a hard link pointing to src named dst.

        :raises FUSEError if the new_parent_inode is not found
        :raises FUSEError if the inode is not found
        """
        logger.debug(f"{new_parent_inode=}//{inode=}")
        parent = self._inode_to_path(new_parent_inode)
        path = parent / fsdecode(new_name)

        try:
            os.link(self._inode_to_path(inode), path, follow_symlinks=False)
        except OSError as exc:
            on_error(exc)
        else:
            self._add_path(inode, path)
            return await self.getattr(inode, ctx)

    async def setattr(
        self,
        inode: InodeT,
        attr: EntryAttributes,
        fields: SetattrFields,
        fh: Optional[FileHandleT],
        ctx: RequestContext,
    ) -> EntryAttributes:
        """Change attributes of inode.

        :raises FUSEError if inode is not found
        """
        attrs = (
            attr.st_size,
            attr.st_mode,
            attr.st_uid,
            attr.st_gid,
            attr.st_atime_ns,
            attr.st_mtime_ns,
        )
        logger.debug(f"{attrs}::{inode} ({fh=})")

        path = self._inode_to_path(inode)
        old_attr = self.lstat(path)

        # create a cache of the file contents to restore
        buffer: memoryview | None = None
        if path.is_file():
            file_fd = os.open(path, os.O_RDONLY)
            content = os.read(file_fd, os.fstat(file_fd).st_size)
            os.lseek(file_fd, 0, 0)
            os.close(file_fd)
            buffer = memoryview(content)

        try:
            if fields.update_size:
                os.truncate(path, attr.st_size)

            if fields.update_mode:
                # Under Linux, chmod always resolves symlinks so we should
                # actually never get a setattr() request for a symbolic
                # link.
                assert not stat_m.S_ISLNK(attr.st_mode)
                os.chmod(path, stat_m.S_IMODE(attr.st_mode))

            if fields.update_uid:
                os.chown(path, attr.st_uid, -1, follow_symlinks=False)

            if fields.update_gid:
                os.chown(path, -1, attr.st_gid, follow_symlinks=False)

            if fields.update_atime and fields.update_mtime:
                if fh is None:
                    os.utime(
                        path,
                        None,
                        follow_symlinks=False,
                        ns=(attr.st_atime_ns, attr.st_mtime_ns),
                    )
                else:
                    os.utime(
                        fh,
                        None,
                        ns=(attr.st_atime_ns, attr.st_mtime_ns),
                    )
            elif fields.update_atime or fields.update_mtime:
                # We can only set both values, so we first need to retrieve the
                # one that we shouldn't be changing.
                if not fields.update_atime:
                    attr.st_atime_ns = old_attr.st_atime_ns
                else:
                    attr.st_mtime_ns = old_attr.st_mtime_ns
                if fh is None:
                    os.utime(
                        path,
                        None,
                        follow_symlinks=False,
                        ns=(attr.st_atime_ns, attr.st_mtime_ns),
                    )
                else:
                    os.utime(
                        fh,
                        None,
                        ns=(attr.st_atime_ns, attr.st_mtime_ns),
                    )
        except OSError as exc:
            logger.error(f"Error occurred: {exc}, Rolling back.", exc_info=exc)
            if path.is_file():
                file_fd = os.open(path, os.O_WRONLY)
                os.write(file_fd, buffer)
                os.close(file_fd)

            if fields.update_mode:
                os.chmod(path, stat_m.S_IMODE(old_attr.st_mode))

            if fields.update_uid or fields.update_gid:
                os.chown(path, old_attr.st_uid, old_attr.st_gid, follow_symlinks=False)

            if fields.update_atime or fields.update_mtime:
                if fh is None:
                    os.utime(
                        path,
                        None,
                        follow_symlinks=False,
                        ns=(old_attr.st_atime_ns, old_attr.st_mtime_ns),
                    )
                else:
                    os.utime(
                        fh,
                        None,
                        ns=(old_attr.st_atime_ns, old_attr.st_mtime_ns),
                    )

            on_error(exc)
        else:
            return self.lstat(path)

    async def mknod(
        self,
        parent_inode: InodeT,
        name: FileNameT,
        mode: ModeT,
        rdev: int,
        ctx: RequestContext,
    ) -> EntryAttributes:
        """Create (possibly special: (file, device special file or named pipe)) file

        :raises FUSEError if the parent_inode is not found
        :raises FUSEError if os.mknod or os.chown cause error
        """
        name = fsdecode(name)
        logger.debug(f"{parent_inode=}//{name=}")
        parent_dir = self._inode_to_path(parent_inode)
        path = parent_dir / name

        try:
            os.mknod(path, mode=(mode & ~ctx.umask), device=rdev)
            os.chown(path, ctx.uid, ctx.gid)
        except OSError as exc:
            on_error(exc)

        attr = self.lstat(path)
        self._add_path(attr.st_ino, path)
        return attr

    async def mkdir(
        self,
        parent_inode: InodeT,
        name: FileNameT,
        mode: ModeT,
        ctx: RequestContext,
    ) -> EntryAttributes:
        """Create a directory

        :raises FUSEError if the parent_inode is not found
        :raises FUSEError if os.mkdir and os.chown cause error
        """
        dir_name = fsdecode(name)
        logger.debug(f"{parent_inode=}//{name=}")
        parent_dir = self._inode_to_path(parent_inode)
        path = parent_dir / dir_name

        try:
            os.mkdir(path, mode=(mode & ~ctx.umask))
            os.chown(path, ctx.uid, ctx.gid)
        except OSError as exc:
            on_error(exc)

        attr = self.lstat(path)
        self._add_path(attr.st_ino, path)
        return attr

    async def statfs(self, ctx: RequestContext) -> StatvfsData:
        """Get file system statistics."""
        logger.debug("Perform statvfs on root")
        root = self._inode_path_map[pyfuse3.ROOT_INODE]
        stat = StatvfsData()
        try:
            statfs = os.statvfs(root)
        except OSError as exc:
            on_error(exc)

        for attr in (
            "f_bsize",
            "f_frsize",
            "f_blocks",
            "f_bfree",
            "f_bavail",
            "f_files",
            "f_ffree",
            "f_favail",
        ):
            setattr(stat, attr, getattr(statfs, attr))

        stat.f_namemax = statfs.f_namemax - (len(root) + 1)
        return stat

    async def open(self, inode: InodeT, flags: FlagT, ctx: RequestContext) -> FileInfo:
        """Open an inode with flags

        This method must return a FileInfo instance.

        The FileInfo.fh field must contain an integer file handle,
        which will be passed to the `read, write, flush, fsync and release` methods
        to identify the open file.

        The FileInfo instance may also have relevant
        configuration attributes set;
        see the FileInfo documentation for more information.

        :raises FUSEError if the inode is not found
        """
        logger.debug(f"{inode=} {flags=}")
        try:
            fd = self._inode_fd_map[inode]
            self._fd_open_count[fd] += 1
            return FileInfo(fh=fd)
        except KeyError:
            assert flags & os.O_CREAT == 0
            try:
                fd = os.open(self._inode_to_path(inode), flags)
            except OSError as exc:
                on_error(exc)
            self._inode_fd_map[inode] = fd
            self._fd_inode_map[fd] = inode
            self._fd_open_count[fd] = 1
            return FileInfo(fh=FileHandleT(fd))

    async def create(
        self,
        parent_inode: InodeT,
        name: FileNameT,
        mode: ModeT,
        flags: FlagT,
        ctx: RequestContext,
    ) -> Tuple[FileInfo, EntryAttributes]:
        """Create a file with permissions mode and open it with flags.

        :raises FUSEError if the parent_inode is not found
        :raises FUSEError if error occurs in os.open
        """
        logger.debug(f"{parent_inode=}, {name=}, {mode=}, {flags=}")

        path = self._inode_to_path(parent_inode) / fsdecode(name)
        try:
            fd = os.open(path, flags | os.O_CREAT | os.O_TRUNC, mode)
        except OSError as exc:
            logger.exception(str(exc), exc_info=exc)
            raise FUSEError(exc.errno)

        entry_attr = self.fstat(fd)
        inode = entry_attr.st_ino
        self._add_path(inode, path)
        self._inode_fd_map[inode] = fd
        self._fd_inode_map[fd] = inode
        self._fd_open_count[fd] = 1

        return FileInfo(FileHandleT(fd)), entry_attr

    async def read(self, fh: FileHandleT, off: int, size: int) -> bytes:
        """Read size bytes from fh at position off.

        fh will be an integer filehandle returned by a prior open or create call.

        This function should return exactly the number of bytes
        requested except on EOF or error,
        otherwise the rest of the data will be substituted with zeroes.
        """
        logger.debug(f"{fh=} from {off} as much as {size}")
        os.lseek(fh, off, os.SEEK_SET)
        return os.read(fh, size)

    async def release(self, fd: FileHandleT) -> None:
        """Release open file

        :raises FUSEError if os.close cause error
        """
        logger.debug(f"{fd=}")

        if self._fd_open_count[fd] > 1:
            self._fd_open_count[fd] -= 1
            return

        del self._fd_open_count[fd]
        inode = self._fd_inode_map[fd]
        del self._inode_fd_map[inode]
        del self._fd_inode_map[fd]
        try:
            os.close(fd)
        except OSError as exc:
            on_error(exc)

    async def write(self, fh: FileHandleT, off: int, buf: bytes) -> int:
        """Write buf into fh at off.

        This method must return the number of bytes written.

        However, unless the file system has been mounted
        with the direct_io option, the file system must
        always write all the provided data (i.e., return len(buf)).
        """
        logger.debug(f"{buf=} at {off=} to {fh=}")
        os.lseek(fh, off, os.SEEK_SET)
        return os.write(fh, buf)

    # async def access(
    #     self,
    #     inode: InodeT,
    #     mode: ModeT,
    #     ctx: RequestContext,
    # ) -> bool:
    #     """Checks the access to the inode
    #
    #     :raises FUSEError if the inode is not found
    #     """
    #     logger.debug(f"Check access to {inode=}::{mode=}")
    #     return os.access(self._inode_to_path(inode), mode)
    #
    # async def flush(self, fh: FileHandleT) -> None:
    #     """Handle close() syscall"""
    #     logger.debug(f"Flush is called on: {fh=}")
    #     await super().flush(fh)
    #
    # async def fsync(self, fh: FileHandleT, datasync: bool) -> None:
    #     """Call fsync syscall
    #
    #     When we implement the s3 layer, we will care about the datasync
    #     https://github.com/s3fs-fuse/s3fs-fuse/blob/master/src/s3fs.cpp#L3146
    #     """
    #     logger.debug(f"fsync is called: {fh=}, {datasync=}")
    #     os.fsync(fh)
    #
    # async def fsyncdir(self, fh: FileHandleT, datasync: bool) -> None:
    #     """fsync an fd if it is pointing to a dir
    #
    #     fd = os.open(dir_path, os.O_DIRECTORY, mode=...)
    #     """
    #     logger.debug(f"fsyncdir is called: {fh=}, {datasync=}")
    #     os.fsync(fh)
    #
    # async def listxattr(self, inode: InodeT, ctx: RequestContext) -> Sequence[XAttrNameT]:
    #     """Get list of extended attributes for inode.
    #
    #     :raises FUSEError if the inode is not found
    #     """
    #     logger.debug(f"Getting xattrs of {inode=}")
    #     if inode in self._inode_fd_map:
    #         xattrs = os.listxattr(self._inode_fd_map[inode])
    #     else:
    #         xattrs = os.listxattr(self._inode_to_path(inode))
    #     return cast(Sequence[XAttrNameT], list(map(str.encode, xattrs)))
    #
    # async def releasedir(self, fd: FileHandleT) -> None:
    #     """Release a directory
    #
    #     :raises FUSEError if os.close cause an error
    #     """
    #     logger.debug(f"Releasing directory: {fd=}")
    #
    #     if self._fd_open_count[fd] > 1:
    #         self._fd_open_count[fd] -= 1
    #         return
    #
    #     del self._fd_open_count[fd]
    #     inode = self._fd_inode_map[fd]
    #     del self._inode_fd_map[inode]
    #     del self._fd_inode_map[fd]
    #     try:
    #         os.close(fd)
    #     except OSError as exc:
    #         on_error(exc)
    #
    # async def removexattr(self, inode: InodeT, name: XAttrNameT, ctx: RequestContext) -> None:
    #     """Remove an xattr
    #
    #     :raises FUSEError if the inode is not found
    #     """
    #     logger.debug(f"Removing xattr of {inode=}")
    #     if inode in self._inode_fd_map:
    #         os.removexattr(self._inode_fd_map[inode], name)
    #     try:
    #         os.removexattr(self._inode_to_path(inode), name)
    #     except FUSEError:
    #         on_error(FUSEError(errno=errno.ENOATTR))
    #
    # async def setxattr(
    #     self,
    #     inode: InodeT,
    #     name: XAttrNameT,
    #     value: bytes,
    #     ctx: RequestContext
    # ) -> None:
    #     """Set extended attribute name of inode to value.
    #
    #     :raises FUSEError if inode is not found
    #     """
    #     logger.debug(f"Setting xattr on {inode=}")
    #     path = self._inode_to_path(inode)
    #
    #     try:
    #         os.setxattr(path, name, value)
    #     except OSError as exc:
    #         on_error(exc)
