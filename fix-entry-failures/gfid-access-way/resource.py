#
# Copyright (c) 2011-2014 Red Hat, Inc. <http://www.redhat.com>
# This file is part of GlusterFS.

# This file is licensed to you under your choice of the GNU Lesser
# General Public License, version 3 or any later version (LGPLv3 or
# later), or the GNU General Public License, version 2 (GPLv2), in all
# cases as published by the Free Software Foundation.
#

import os
import sys
import stat
import time
import struct
import random
import xattr
import types
from datetime import datetime

from errno import EEXIST, ENOENT, ESTALE, EBUSY, EISDIR, EINVAL

GX_GFID_CANONICAL_LEN = 37  # canonical gfid len + '\0'

errlog = open("sync_err.log", 'a')

def entry2pb(e):
    return e.rsplit('/', 1)

def umask():
    return os.umask(0)

def _fmt_mknod(l):
    return "!II%dsI%dsIII" % (37, l+1)

def _fmt_mkdir(l):
    return "!II%dsI%dsII" % (37, l+1)

def _fmt_symlink(l1, l2):
    return "!II%dsI%ds%ds" % (37, l1+1, l2+1)

def entry_ops(mntpt, entry, fix_gfid):
    pfx = ".gfid"
    # regular file
    def entry_pack_reg(gf, bn, mo, uid, gid):
        blen = len(bn)
        return struct.pack(_fmt_mknod(blen),
                           uid, gid, gf, mo, bn,
                           stat.S_IMODE(mo), 0, umask())

    def entry_pack_reg_stat(gf, bn, st):
        blen = len(bn)
        mo = st['mode']
        return struct.pack(_fmt_mknod(blen),
                           st['uid'], st['gid'],
                           gf, mo, bn,
                           stat.S_IMODE(mo), 0, umask())
    # mkdir

    def entry_pack_mkdir(gf, bn, mo, uid, gid):
        blen = len(bn)
        return struct.pack(_fmt_mkdir(blen),
                           uid, gid, gf, mo, bn,
                           stat.S_IMODE(mo), umask())
    # symlink

    def entry_pack_symlink(gf, bn, lnk, st):
        blen = len(bn)
        llen = len(lnk)
        return struct.pack(_fmt_symlink(blen, llen),
                           st['uid'], st['gid'],
                           gf, st['mode'], bn, lnk)

    def errno_wrap(call, arg=[], errnos=[], retry_errnos=[]):
        """ wrapper around calls resilient to errnos.
        """
        nr_tries = 0
        while True:
            try:
                return call(*arg)
            except OSError:
                ex = sys.exc_info()[1]
                if ex.errno in errnos:
                    return ex.errno
                if not ex.errno in retry_errnos:
                    raise
                nr_tries += 1
                if nr_tries == 5:
                    # probably a screwed state, cannot do much...
                    print('reached maximum retries (%s)...%s' %
                                 (repr(arg), ex))
                    raise
                time.sleep(0.250)  # retry the call

    def lstat(e):
        return errno_wrap(os.lstat, [e], [ENOENT], [ESTALE, EBUSY])

    def gfid_mnt(gfidpath):
        try:
            return xattr.get(gfidpath, "glusterfs.gfid.string", nofollow=True)
        except IOError:
            ex = sys.exc_info()[1][0]
            if ex in [ENOENT]:
                return ex
            else:
                raise

    def xattr_set(path, key, blob, errnos=[], retry_errnos=[]):
        nr_tries = 0
        while True:
            try:
                xattr.set(path, key, blob, nofollow=True)
            except IOError:
                ex = sys.exc_info()[1][0]
                if ex in errnos:
                    return ex
                if not ex in retry_errnos:
                    raise
                nr_tries += 1
                if nr_tries == 5:
                    # probably a screwed state, cannot do much...
                    print('reached maximum retries (%s)...%s' %
                                 (repr(arg), ex))
                    raise
                time.sleep(0.250)  # retry the call

    def matching_disk_gfid(gfid, entry):
        disk_gfid = gfid_mnt(entry)
        if isinstance(disk_gfid, int):
            return False

        if not gfid == disk_gfid:
            return False

        return True

    def rename_with_disk_gfid_confirmation(gfid, entry, en):
        if not matching_disk_gfid(gfid, entry):
            print("RENAME ignored: source entry does not match "
                  "with on-disk gfid")
            errlog.write ("%s" % repr(e))
            return

        cmd_ret = errno_wrap(os.rename,
                             [entry, en],
                             [ENOENT, EEXIST], [ESTALE, EBUSY])
        if not cmd_ret:
            print "Fop RENAME successful"
        else:
            print "Fop RENAME Failed : %s" % cmd_ret
            errlog.write ("%s" % repr(e))

    os.chdir(mntpt)
    e = entry

    blob = None
    op = e['op']
    gfid = e['gfid']
    entry = e['entry']
    uid = 0
    gid = 0
    if e.get("stat", {}):
        # Copy UID/GID value and then reset to zero. Copied UID/GID
        # will be used to run chown once entry is created.
        uid = e['stat']['uid']
        gid = e['stat']['gid']
        e['stat']['uid'] = 0
        e['stat']['gid'] = 0

    (pg, bname) = entry2pb(entry)
    if op in ['RMDIR', 'UNLINK']:
        print "RMDIR/UNLINK, Not supported"
    elif op in ['CREATE', 'MKNOD']:
        blob = entry_pack_reg(gfid, bname, e['mode'], e['uid'], e['gid'])
    elif op == 'MKDIR':
        blob = entry_pack_mkdir(gfid, bname, e['mode'], e['uid'], e['gid'])
    elif op == 'LINK':
        slink = os.path.join(pfx, gfid)
        st = lstat(slink)
        if isinstance(st, int):
            (pg, bname) = entry2pb(entry)
            blob = entry_pack_reg_stat(gfid, bname, e['stat'])
        else:
            cmd_ret = errno_wrap(os.link,
                                 [slink, entry],
                                 [ENOENT, EEXIST], [ESTALE])
            if not cmd_ret:
                print "Fop LINK successful"
            else:
                print "Fop LINK Failed : %s" % cmd_ret
                errlog.write ("%s" % repr(e))
    elif op == 'SYMLINK':
        blob = entry_pack_symlink(gfid, bname, e['link'], e['stat'])
    elif op == 'RENAME':
        en = e['entry1']
        #stat on source
        st = lstat(entry)
        if isinstance(st, int):
            if e['stat'] and not stat.S_ISDIR(e['stat']['mode']):
                if stat.S_ISLNK(e['stat']['mode']) and \
                   e['link'] is not None:
                    (pg, bname) = entry2pb(en)
                    blob = entry_pack_symlink(gfid, bname,
                                              e['link'], e['stat'])
                else:
                    (pg, bname) = entry2pb(en)
                    blob = entry_pack_reg_stat(gfid, bname, e['stat'])
        else:
            #stat on dest
            st1 = lstat(en)
            if isinstance(st1, int):
                rename_with_disk_gfid_confirmation(gfid, entry, en)
            else:
                if st.st_ino == st1.st_ino:
                    # we have a hard link, we can now unlink source
                    try:
                        errno_wrap(os.unlink, [entry],
                                   [ENOENT, ESTALE], [EBUSY])
                    except OSError as e:
                        if e.errno == EISDIR:
                            try:
                                errno_wrap(os.rmdir, [entry],
                                           [ENOENT, ESTALE], [EBUSY])
                            except OSError as e:
                                if e.errno == ENOTEMPTY:
                                    print("Unable to delete directory"
                                           ", Both Old and New"
                                           " directories exists")
                                else:
                                    raise
                        else:
                            raise
                else:
                    rename_with_disk_gfid_confirmation(gfid, entry, en)
    if blob:
        if os.path.lexists(e['entry']) and \
            str(gfid) != xattr.get(e['entry'], "glusterfs.gfid.string", nofollow=True):
            print "GFID MISMATCH: Fixing..Unlinking...: %s" % e['entry']
            if os.path.isdir(e['entry']):
                os.rmdir(e['entry'])
            else:
                os.unlink(e['entry'])
                if fix_gfid:
                    errlog.write("%s: Failed to fix gfid=%s\n" % (datetime.now(), fix_gfid))

        cmd_ret = xattr_set(pg, 'glusterfs.gfid.newfile', blob,
                             [EEXIST, ENOENT],
                             [ESTALE, EINVAL, EBUSY])
        if not cmd_ret in [EEXIST]:
            print "Fop: %s failed Reason:%s " % (op, cmd_ret)
            errlog.write("%s" % repr(e))
        else:
            print "Fop: %s successful" % op

        # If UID/GID is different than zero that means we are trying
        # create Entry with different UID/GID. Create Entry with
        # UID:0 and GID:0, and then call chown to set UID/GID
        if uid != 0 or gid != 0:
            path = os.path.join(pfx, gfid)
            cmd_ret = errno_wrap(os.chown, [path, uid, gid], [ENOENT],
                                 [ESTALE, EINVAL])
            if cmd_ret:
                    print "Setting uid/gid failed for %s:%s" % (op, path)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("USAGE: %s <mount> <entry set>" % (sys.argv[0]))
        sys.exit(-1)

    mnt = sys.argv[1]
    entry = sys.argv[2]
    entry = eval(entry)
    entry_ops(mnt, entry)
